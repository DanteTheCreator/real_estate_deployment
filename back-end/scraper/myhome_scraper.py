"""
Advanced MyHome.ge Property Scraper - Refactored Version

This is the main scraper class that orchestrates all components to scrape
property data from MyHome.ge with advanced features like multilingual support,
deduplication, and comprehensive error handling.

Author: Production Team
Version: 2.0.0 (Refactored)
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
from sqlalchemy.orm import Session

# Import with fallbacks for Docker compatibility
try:
    from .core.config import ScrapingConfig
    from .core.base_scraper import BaseScraper
    from .models.property_data import PropertyData
    from .models.statistics import ScrapingStats
    from .processors.data_processor import DataProcessor
    from .processors.image_processor import ImageProcessor
    from .processors.multilingual_processor import MultilingualProcessor
    from .processors.parameter_processor import ParameterProcessor
    from .processors.price_processor import PriceProcessor
    from .services.database_service import DatabaseService
    from .services.deduplication_service import DeduplicationService
    from .services.report_service import ReportService
except ImportError:
    try:
        from core.config import ScrapingConfig
        from core.base_scraper import BaseScraper
        from models.property_data import PropertyData
        from models.statistics import ScrapingStats
        from processors.data_processor import DataProcessor
        from processors.image_processor import ImageProcessor
        from processors.multilingual_processor import MultilingualProcessor
        from processors.parameter_processor import ParameterProcessor
        from processors.price_processor import PriceProcessor
        from services.database_service import DatabaseService
        from services.deduplication_service import DeduplicationService
        from services.report_service import ReportService
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.core.base_scraper import BaseScraper
        from scraper.models.property_data import PropertyData
        from scraper.models.statistics import ScrapingStats
        from scraper.processors.data_processor import DataProcessor
        from scraper.processors.image_processor import ImageProcessor
        from scraper.processors.multilingual_processor import MultilingualProcessor
        from scraper.processors.parameter_processor import ParameterProcessor
        from scraper.processors.price_processor import PriceProcessor
        from scraper.services.database_service import DatabaseService
        from scraper.services.deduplication_service import DeduplicationService
        from scraper.services.report_service import ReportService


class MyHomeAdvancedScraper(BaseScraper):
    """Advanced MyHome.ge scraper with modular architecture."""
    
    def __init__(self, config: ScrapingConfig = None):
        """Initialize the scraper with all components."""
        if config is None:
            config = ScrapingConfig()
        
        super().__init__(config)
        
        # Initialize processors
        self.data_processor = DataProcessor(config)
        self.multilingual_processor = MultilingualProcessor(config)
        self.image_processor = ImageProcessor(config)
        self.price_processor = PriceProcessor(config)
        self.parameter_processor = ParameterProcessor(config)
        
        # Initialize services
        self.database_service = DatabaseService(config)
        self.deduplication_service = DeduplicationService(config)
        self.report_service = ReportService(config)
        
        # Create necessary directories
        self.create_directories()
        
        self.logger.info("MyHome.ge Advanced Scraper initialized successfully")
    
    async def scrape(self, property_type_filter: Optional[int] = None,
                    deal_type_filter: Optional[int] = None) -> ScrapingStats:
        """Main scraping method with full multilingual support."""
        self.logger.info("Starting full scraping mode")
        
        db = self.database_service.get_session()
        try:
            # Create default user
            default_user = self.database_service.create_default_user(db)
            
            # Cleanup old properties
            cleaned = self.database_service.cleanup_old_properties(db)
            self.stats.cleaned_old = cleaned
            
            # Start scraping
            await self._scrape_properties(
                db, default_user, property_type_filter, deal_type_filter
            )
            
            # Cleanup orphaned images if enabled
            if self.config.enable_image_download:
                active_ids = self.database_service.get_active_property_ids(db)
                self.image_processor.cleanup_orphaned_images(active_ids)
            
        except Exception as e:
            self.logger.error(f"Critical error in scraping process: {e}")
            self.stats.errors += 1
            raise RuntimeError(f"Scraping failed: {e}")
        
        finally:
            db.close()
            self.finalize()
        
        return self.stats
    
    async def _scrape_properties(self, db: Session, default_user, 
                               property_type_filter: Optional[int],
                               deal_type_filter: Optional[int]) -> None:
        """Scrape properties with pagination and processing."""
        properties_processed = 0
        page = 1
        
        # Create aiohttp session for multilingual extraction
        async with aiohttp.ClientSession() as async_session:
            while properties_processed < self.config.max_properties:
                try:
                    # Fetch properties page
                    data = await self._fetch_properties_page(
                        page, property_type_filter, deal_type_filter
                    )
                    
                    if not data or not data.get('data'):
                        self.logger.info("No more properties to fetch")
                        break
                    
                    properties = data['data']
                    self.stats.total_fetched += len(properties)
                    
                    self.logger.info(f"🔄 Page {page}: Fetched {len(properties)} properties")
                    
                    # Process each property
                    for raw_property in properties:
                        try:
                            await self._process_single_property(
                                db, async_session, raw_property, default_user
                            )
                                
                        except Exception as e:
                            self.logger.error(f"Error processing property {raw_property.get('id', 'unknown')}: {e}")
                            self.stats.errors += 1
                            continue
                    
                    properties_processed += len(properties)
                    
                    page += 1
                    
                    self.logger.info(f"📋 Page {page-1}: Processed {len(properties)} properties")
                    
                    # Progress logging
                    if properties_processed % 100 == 0:
                        self.logger.info(f"📊 Total progress: {properties_processed} properties processed")
                    
                    # Respect rate limits
                    await asyncio.sleep(self.config.delay_between_requests)
                    
                    # Break if we got no properties (empty page) or significantly fewer than expected
                    # API can return up to 1000 properties per page with per_page parameter
                    per_page = getattr(self.config, 'per_page', 1000)
                    if len(properties) == 0:
                        self.logger.info(f"🛑 Received 0 properties - last page reached")
                        break
                    elif len(properties) < per_page * 0.1:  # Less than 10% of requested page size
                        self.logger.info(f"🛑 Received {len(properties)} properties (less than 10% of page size {per_page}) - likely last page reached")
                        break
                
                except Exception as e:
                    self.logger.error(f"Error fetching page {page}: {e}")
                    self.stats.errors += 1
                    break
    
    async def _fetch_properties_page(self, page: int, 
                                   property_type_filter: Optional[int],
                                   deal_type_filter: Optional[int]) -> Optional[Dict]:
        """Fetch a page of properties from the API."""
        # Use configured default property types or fallback to all types
        default_property_types = getattr(self.config, 'default_property_types', "2,1,3,4,5,6")
        default_deal_types = getattr(self.config, 'default_deal_types', "1,2,3,7")
        per_page = getattr(self.config, 'per_page', 1000)
        
        params = {
            'currency_id': 1,  # USD
            'deal_types': deal_type_filter or default_deal_types,  # Default to all deal types
            'real_estate_types': property_type_filter or default_property_types,  # Default to all types
            'page': page,
            'per_page': per_page  # Get maximum properties per request
        }
        
        self.logger.debug(f"🌐 Fetching page {page} with params: {params}")
        
        try:
            response = self.make_request(
                self.config.api_endpoints['list_properties'],
                params=params
            )
            
            data = response.json()
            
            if data.get('result') and data.get('data') and data['data'].get('data'):
                properties = data['data']['data']  # Navigate to the actual properties array
                self.logger.info(f"📥 Successfully fetched {len(properties)} properties from page {page}")
                
                # Log first property ID for debugging pagination
                if properties:
                    first_id = properties[0].get('id', 'unknown')
                    last_id = properties[-1].get('id', 'unknown')
                    self.logger.info(f"📋 Page {page} - Property range: {first_id} to {last_id}")
                
                return {'result': True, 'data': properties}
            else:
                self.logger.warning(f"⚠️ No data returned from API for page {page}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch page {page}: {e}")
            self.stats.errors += 1
            return None
    
    async def _process_single_property(self, db: Session, async_session: aiohttp.ClientSession,
                                     raw_data: Dict, default_user) -> None:
        """Process a single property through all stages."""
        # Step 1: Basic data processing
        property_data = self.data_processor.process_property(raw_data)
        if not property_data:
            return
        
        # Step 2: Check for duplicates
        duplicates = self.deduplication_service.find_duplicates(db, property_data)
        
        if duplicates:
            existing_property = duplicates[0]
            
            if self.deduplication_service.should_replace_duplicate(property_data, existing_property):
                self.logger.info(f"Replacing agency listing with owner listing for property {property_data.external_id}")
                db.delete(existing_property)
                db.flush()
                self.stats.agency_discarded += 1
            else:
                self.logger.debug(f"Skipping duplicate property {property_data.external_id}")
                self.stats.duplicates_skipped += 1
                return
        
        # Step 3: Enhanced processing
        await self._enhance_property_data(async_session, property_data, raw_data)
        
        # Step 4: Save to database
        saved_property = self._save_property_to_database(db, property_data, default_user)
        
        property_id = property_data.external_id
        self.logger.info(f"🔄 Processing single property: {property_id}")
        
        if saved_property:
            # Update statistics
            if saved_property.created_at.date() == datetime.now().date():
                self.stats.new_properties += 1
                self.logger.info(f"🆕 Property {property_id} marked as NEW")
            else:
                self.stats.updated_properties += 1
                self.logger.info(f"🔄 Property {property_id} marked as UPDATED")
            
            # Track property and deal types
            self.stats.add_property_type(property_data.property_type)
            self.stats.add_deal_type(property_data.listing_type)
            
            # Track owner prioritization
            if self.deduplication_service.is_owner_listing(property_data):
                self.stats.owner_prioritized += 1
                self.logger.debug(f"👤 Property {property_id} prioritized as owner listing")
        else:
            self.logger.warning(f"⚠️ Property {property_id} was not saved to database")
    
    async def _enhance_property_data(self, async_session: aiohttp.ClientSession,
                                   property_data: PropertyData, raw_data: Dict) -> None:
        """Enhance property data with additional processing."""
        try:
            # Process multilingual content
            await self.multilingual_processor.process_multilingual_content(
                async_session, property_data
            )
            
            # Process images
            self.image_processor.process_property_images(property_data, raw_data)
            
            # Process prices
            self.price_processor.process_property_prices(property_data, raw_data)
            
            # Process parameters
            self.parameter_processor.process_property_parameters(property_data, raw_data)
            
        except Exception as e:
            self.logger.warning(f"Error enhancing property {property_data.external_id}: {e}")
    
    def _save_property_to_database(self, db: Session, property_data: PropertyData, 
                                 default_user) -> Optional:
        """Save property data to database."""
        try:
            # Check if property already exists
            existing_property = self.database_service.find_existing_property(
                db, property_data.external_id
            )
            
            if existing_property:
                # Update existing property
                return self.database_service.update_property(db, existing_property, property_data)
            else:
                # Create new property
                return self.database_service.save_property(db, property_data, default_user)
                
        except RuntimeError as e:
            self.logger.error(f"Database error saving property {property_data.external_id}: {e}")
            self.stats.errors += 1
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error saving property {property_data.external_id}: {e}")
            self.stats.errors += 1
            return None
    
    def validate_property_data(self, property_data: PropertyData) -> bool:
        """Always return True - no validation needed for MyHome.ge data."""
        return True
    
    def generate_report(self, output_format: str = "json") -> str:
        """Generate comprehensive scraping report."""
        try:
            # Update languages processed in stats
            if self.multilingual_processor.is_multilingual_enabled():
                self.stats.languages_processed = self.multilingual_processor.get_supported_languages()
            
            return self.report_service.generate_report(self.stats, output_format)
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise RuntimeError(f"Report generation failed: {e}")
    
    def get_statistics(self) -> ScrapingStats:
        """Get current scraping statistics."""
        return self.stats
    
    def get_configuration(self) -> Dict:
        """Get current configuration."""
        return self.config.to_dict()


# Convenience functions for backwards compatibility
async def scrape_properties(config: ScrapingConfig = None, 
                          **kwargs) -> ScrapingStats:
    """Convenience function to run the scraper."""
    scraper = MyHomeAdvancedScraper(config)
    try:
        return await scraper.scrape(**kwargs)
    finally:
        scraper.finalize()


def create_scraper_from_config_file(config_path: str) -> MyHomeAdvancedScraper:
    """Create scraper instance from configuration file."""
    config = ScrapingConfig.from_file(config_path)
    return MyHomeAdvancedScraper(config)


def create_scraper_from_env() -> MyHomeAdvancedScraper:
    """Create scraper instance from environment variables."""
    config = ScrapingConfig.from_env()
    return MyHomeAdvancedScraper(config)


if __name__ == "__main__":
    """Run the scraper when executed directly."""
    import asyncio
    
    async def main():
        """Main execution function."""
        try:
            # Create scraper with default config
            scraper = MyHomeAdvancedScraper()
            
            # Run continuous scraping
            while True:
                print("Starting scraping cycle...")
                stats = await scraper.scrape()
                
                print(f"Scraping completed - New: {stats.new_properties}, Updated: {stats.updated_properties}, Errors: {stats.errors}")
                
                # Wait 1 second before next cycle
                print("Waiting 1 second before next cycle...")
                await asyncio.sleep(1)  # 1 second
                
        except KeyboardInterrupt:
            print("Scraper stopped by user")
        except Exception as e:
            print(f"Scraper error: {e}")
            raise
    
    # Run the main function
    asyncio.run(main())
