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
    
    # Import database models for bulk operations
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import Property
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
        
        # Import database models for bulk operations  
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database import Property
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
        
        # Import database models for bulk operations
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from database import Property


class MyHomeAdvancedScraper(BaseScraper):
    """Advanced MyHome.ge scraper with modular architecture."""
    
    def __init__(self, config: ScrapingConfig = None):
        """Initialize the MAXIMUM SPEED scraper."""
        if config is None:
            config = ScrapingConfig()
        
        # Override config for MAXIMUM SPEED
        config.max_properties = 999999999  # No limit
        config.per_page = 1000  # Maximum per page
        config.batch_size = 999999999  # No batching
        
        super().__init__(config)
        
        # Initialize only essential processors
        self.data_processor = DataProcessor(config)
        
        # Initialize only essential services
        self.database_service = DatabaseService(config)
        self.deduplication_service = DeduplicationService(config)
        
        # Track seen property IDs
        self.seen_property_ids = set()
        
        self.logger.info("MAXIMUM SPEED scraper initialized - NO LIMITS")
    
    async def scrape(self) -> ScrapingStats:
        """Main MAXIMUM SPEED scraping method - NO LIMITS."""
        self.logger.info("Starting MAXIMUM SPEED scraping - NO BATCH LIMITS")
        
        # Reset seen properties
        self.seen_property_ids.clear()
        
        db = self.database_service.get_session()
        try:
            # Create default user
            default_user = self.database_service.create_default_user(db)
            
            # Start MAXIMUM SPEED scraping
            await self._scrape_properties(db, default_user)
            
        except Exception as e:
            self.logger.error(f"Critical error in scraping: {e}")
            self.stats.errors += 1
            raise RuntimeError(f"Scraping failed: {e}")
        
        finally:
            db.close()
        
        return self.stats
    
    async def _scrape_properties(self, db: Session, default_user) -> None:
        """MAXIMUM SPEED property scraping - NO LIMITS."""
        properties_processed = 0
        page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        async with aiohttp.ClientSession() as async_session:
            while consecutive_empty_pages < max_consecutive_empty:
                try:
                    # Fetch properties page
                    data = await self._fetch_properties_page(page)
                    
                    if not data or not data.get('data'):
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= max_consecutive_empty:
                            break
                        page += 1
                        continue
                    
                    properties = data['data']
                    
                    if len(properties) == 0:
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= max_consecutive_empty:
                            break
                        page += 1
                        continue
                    
                    consecutive_empty_pages = 0
                    self.stats.total_fetched += len(properties)
                    
                    # Filter new properties ULTRA-FAST
                    new_properties = []
                    for raw_property in properties:
                        property_id = raw_property.get('id')
                        if property_id and str(property_id) not in self.seen_property_ids:
                            self.seen_property_ids.add(str(property_id))
                            new_properties.append(raw_property)
                    
                    self.logger.info(f"Page {page}: {len(new_properties)}/{len(properties)} new properties")
                    
                    if new_properties:
                        # Process ALL properties from this page at MAXIMUM SPEED
                        processed_count = await self._process_properties_batch(
                            db, async_session, new_properties, default_user
                        )
                    
                    properties_processed += len(properties)
                    
                    # Check for repeated data
                    if len(new_properties) == 0:
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= max_consecutive_empty:
                            break
                    
                    page += 1
                    
                    # Check if fewer properties than requested (last page)
                    if len(properties) < self.config.per_page:
                        break
                
                except Exception as e:
                    self.logger.error(f"Error fetching page {page}: {e}")
                    self.stats.errors += 1
                    consecutive_empty_pages += 1
                    if consecutive_empty_pages >= max_consecutive_empty:
                        break
                    page += 1
                    continue
            
            self.logger.info(f"MAXIMUM SPEED scraping completed: {properties_processed} properties processed")
    
    async def _fetch_properties_page(self, page: int) -> Optional[Dict]:
        """Fetch properties page - speed optimized."""
        params = {
            'currency_id': 1,
            'deal_types': self.config.default_deal_types,
            'real_estate_types': self.config.default_property_types,
            'page': page,
            'per_page': self.config.per_page
        }
        
        try:
            response = self.make_request(
                self.config.api_endpoints['list_properties'],
                params=params
            )
            
            data = response.json()
            
            if data.get('result') and data.get('data') and data['data'].get('data'):
                properties = data['data']['data']
                return {'result': True, 'data': properties}
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to fetch page {page}: {e}")
            self.stats.errors += 1
            return None
    
    async def _process_single_property(self, db: Session, async_session: aiohttp.ClientSession,
                                     raw_data: Dict, default_user) -> None:
        """Process a single property through all stages."""
        # Step 1: Basic data processing
        property_data = self.data_processor.process_property(raw_data)
        if not property_data:
            return
        
        property_id = property_data.external_id
        
        # Step 2: Check for duplicates
        duplicates = self.deduplication_service.find_duplicates(db, property_data)
        
        if duplicates:
            existing_property = duplicates[0]
            
            if self.deduplication_service.should_replace_duplicate(property_data, existing_property):
                self.logger.info(f"Replacing agency listing with owner listing for property {property_id}")
                db.delete(existing_property)
                db.flush()
                self.stats.agency_discarded += 1
            else:
                self.stats.duplicates_skipped += 1
                return  # Skip processing this duplicate
        
        # Step 3: Enhanced processing
        await self._enhance_property_data(async_session, property_data, raw_data)
        
        # Step 4: Save to database
        saved_property = self._save_property_to_database(db, property_data, default_user)
        
        if saved_property:
            # Update statistics based on whether this is truly a new property
            if saved_property.created_at.date() == datetime.now().date():
                self.stats.new_properties += 1
            else:
                self.stats.updated_properties += 1
            
            # Track property and deal types
            self.stats.add_property_type(property_data.property_type)
            self.stats.add_deal_type(property_data.listing_type)
            
            # Track owner prioritization
            if self.deduplication_service.is_owner_listing(property_data):
                self.stats.owner_prioritized += 1
        else:
            self.logger.warning(f"⚠️ Property {property_id} was not saved to database")
    
    async def _process_properties_batch(self, db: Session, async_session: aiohttp.ClientSession,
                                      raw_properties: List[Dict], default_user) -> int:
        """Process properties in controlled batches to prevent database overload."""
        total_count = len(raw_properties)
        processed_count = 0
        
        # Use maximum batch size for optimal performance with controlled delay
        BATCH_SIZE = 1000  # Maximum batch size for optimal throughput
        
        self.logger.info(f"🏭 CONTROLLED BATCH MODE: Processing {total_count} properties in batches of {BATCH_SIZE}")
        
        # Process properties in maximum batches with controlled delays
        for i in range(0, total_count, BATCH_SIZE):
            batch = raw_properties[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            self.logger.info(f"Processing batch {batch_num}: {len(batch)} properties")
            
            try:
                # Process batch with controlled database access
                batch_processed = await self._process_single_batch(db, async_session, batch, default_user)
                processed_count += batch_processed
                
                # Force commit after each batch to prevent long-running transactions
                db.commit()
                self.logger.debug(f"Committed batch {batch_num} to database")
                
                # 3 second delay between batches to balance load
                await asyncio.sleep(3.0)  # 3 second delay between batches
                
            except Exception as e:
                self.logger.error(f"Error processing batch {batch_num}: {e}")
                db.rollback()  # Rollback failed batch
                continue
        
        self.logger.info(f"✅ BATCH PROCESSING COMPLETE: {processed_count} properties saved")
        return processed_count
    
    async def _process_single_batch(self, db: Session, async_session: aiohttp.ClientSession,
                                  raw_properties: List[Dict], default_user) -> int:
        """Process a single batch of properties."""
        
        # Process ALL properties directly without any batching or delays
        valid_properties = []
        existing_dict = {}
        processed_count = 0
        
        # ULTRA-FAST bulk duplicate check - single query for ALL properties
        if raw_properties:
            external_ids = [str(prop.get('id', '')) for prop in raw_properties]
            existing_properties = db.query(Property).filter(
                Property.external_id.in_(external_ids)
            ).all()
            existing_dict = {str(prop.external_id): prop for prop in existing_properties}
        
        # DIRECT PROCESSING - NO LOOPS, NO DELAYS
        for raw_property in raw_properties:
            try:
                property_data = self.data_processor.process_property(raw_property)
                if not property_data:
                    continue
                
                property_id = str(property_data.external_id)
                
                # Ultra-fast duplicate check
                if property_id in existing_dict:
                    existing_property = existing_dict[property_id]
                    if (self.config.enable_owner_priority and 
                        self.deduplication_service.is_owner_listing(property_data) and
                        not self._is_owner_listing_from_db(existing_property)):
                        db.delete(existing_property)
                        self.stats.agency_discarded += 1
                    else:
                        self.stats.duplicates_skipped += 1
                        continue
                
                valid_properties.append(property_data)
                
            except Exception as e:
                self.logger.error(f"Error processing property {raw_property.get('id', 'unknown')}: {e}")
                self.stats.errors += 1
                continue
        
        # BULK SAVE ALL at once - MAXIMUM DATABASE EFFICIENCY
        if valid_properties:
            saved_count = self._ultra_fast_bulk_save(db, valid_properties, default_user)
            processed_count += saved_count
            
            # Update statistics in bulk
            for property_data in valid_properties[:saved_count]:
                self.stats.add_property_type(property_data.property_type)
                self.stats.add_deal_type(property_data.listing_type)
                if self.deduplication_service.is_owner_listing(property_data):
                    self.stats.owner_prioritized += 1
        
        # Single commit for ALL properties
        db.commit()
        self.logger.info(f"✅ MAXIMUM SPEED: {processed_count} properties saved in single operation")
        
        return processed_count
    
    def _ultra_fast_bulk_save(self, db: Session, properties: List[PropertyData], default_user) -> int:
        """ULTRA-FAST bulk save - MAXIMUM SPEED."""
        saved_count = 0
        
        # Direct database insertion without checks
        for property_data in properties:
            try:
                # Create property dict
                property_dict = property_data.to_dict()
                property_dict['owner_id'] = default_user.id
                
                # Direct database insertion
                property_obj = Property(**property_dict)
                db.add(property_obj)
                db.flush()  # Get ID
                
                # Save related data directly
                self.database_service._save_property_images(db, property_obj.id, property_data.images)
                self.database_service._save_property_parameters(db, property_obj.id, property_data.parameters)
                self.database_service._save_property_prices(db, property_obj.id, property_data.prices)
                
                saved_count += 1
                self.stats.new_properties += 1
                        
            except Exception as e:
                self.logger.error(f"Error in ultra-fast save for property {property_data.external_id}: {e}")
                self.stats.errors += 1
                continue
        
        return saved_count
    
    def _batch_save_properties(self, db: Session, properties: List[PropertyData], default_user) -> int:
        """Save multiple properties to database efficiently."""
        saved_count = 0
        
        for property_data in properties:
            try:
                # Check if property already exists
                existing_property = self.database_service.find_existing_property(
                    db, property_data.external_id
                )
                
                if existing_property:
                    # Update existing property
                    updated_property = self.database_service.update_property(db, existing_property, property_data)
                    if updated_property:
                        saved_count += 1
                        self.stats.updated_properties += 1
                else:
                    # Create new property
                    new_property = self.database_service.save_property(db, property_data, default_user)
                    if new_property:
                        saved_count += 1
                        self.stats.new_properties += 1
                        
            except Exception as e:
                self.logger.error(f"Error saving property {property_data.external_id}: {e}")
                self.stats.errors += 1
                continue
        
        return saved_count
    
    async def _enhance_property_data(self, async_session: aiohttp.ClientSession,
                                   property_data: PropertyData, raw_data: Dict) -> None:
        """Skip all enhancements for MAXIMUM SPEED."""
        # Skip ALL enhancements for maximum speed - direct data processing only
        pass
    
    def get_statistics(self) -> ScrapingStats:
        """Get current scraping statistics."""
        return self.stats
    
    def validate_property_data(self, property_data: Dict) -> bool:
        """Validate property data - minimal implementation."""
        return property_data is not None and 'id' in property_data
    
    def _is_owner_listing_from_db(self, db_property) -> bool:
        """Check if a database property is an owner listing."""
        # Simple check - owner listings typically have specific patterns
        if hasattr(db_property, 'agency_name') and db_property.agency_name:
            # If it has agency_name, it's likely an agency listing
            return False
        return True  # Assume owner listing if no agency info


if __name__ == "__main__":
    """Run the MAXIMUM SPEED scraper."""
    import asyncio
    
    async def main():
        """Main execution function - MAXIMUM SPEED MODE."""
        try:
            scraper = MyHomeAdvancedScraper()
            
            cycle_count = 0
            while True:
                cycle_count += 1
                print(f"MAXIMUM SPEED Cycle #{cycle_count}...")
                stats = await scraper.scrape()
                
                print(f"New: {stats.new_properties}, Updated: {stats.updated_properties}, Errors: {stats.errors}")
                
                # NO DELAY - MAXIMUM SPEED CONTINUOUS SCRAPING
                # await asyncio.sleep(1)  # Removed for maximum speed
                
        except KeyboardInterrupt:
            print("MAXIMUM SPEED scraper stopped")
        except Exception as e:
            print(f"Error: {e}")
            raise
    
    asyncio.run(main())
