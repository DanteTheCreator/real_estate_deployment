#!/usr/bin/env python3
"""
Standalone multilingual content processor.

This script runs independently from the main scraper to process multilingual
content for properties. It pulls property IDs from a queue or database
and processes them for English and Russian translations.

Usage:
    python multilingual_worker.py [--config-file config.yaml] [--batch-size 10] [--continuous]
"""

import argparse
import asyncio
import aiohttp
import logging
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

# Add parent directories to path for Docker compatibility
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import Property, SessionLocal
    from scraper.core.config import ScrapingConfig
    from scraper.processors.multilingual_processor import MultilingualProcessor
    from scraper.models.property_data import PropertyData
except ImportError:
    # Fallback for direct execution
    sys.path.append('/app')
    from database import Property, SessionLocal
    from scraper.core.config import ScrapingConfig
    from scraper.processors.multilingual_processor import MultilingualProcessor
    from scraper.models.property_data import PropertyData

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func


@dataclass
class ProcessingStats:
    """Statistics for multilingual processing."""
    processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def get_elapsed_time(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_processing_rate(self) -> float:
        elapsed = self.get_elapsed_time()
        return self.processed / elapsed if elapsed > 0 else 0.0


class MultilingualWorker:
    """Standalone worker for processing multilingual content."""
    
    def __init__(self, config: ScrapingConfig, batch_size: int = 10):
        """Initialize the multilingual worker."""
        self.config = config
        self.batch_size = batch_size
        self.logger = self._setup_logging()
        self.multilingual_processor = MultilingualProcessor(config)
        self.stats = ProcessingStats()
        
        # Processing controls
        self.running = True
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the worker."""
        logger = logging.getLogger('MultilingualWorker')
        logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def get_properties_needing_translation(self, db: Session, limit: int = None) -> List[Property]:
        """
        Get properties that need multilingual processing.
        
        Criteria:
        - Properties that don't have English or Russian translations
        - Properties that were recently scraped (within last 7 days)
        - Properties that are available for rent
        """
        limit = limit or self.batch_size
        
        query = db.query(Property).filter(
            and_(
                Property.is_available == True,
                Property.listing_type == 'rent',
                or_(
                    Property.title_en.is_(None),
                    Property.title_ru.is_(None),
                    Property.description_en.is_(None),
                    Property.description_ru.is_(None)
                ),
                # Only process recently scraped properties (within 7 days)
                Property.created_at >= datetime.now() - timedelta(days=7)
            )
        ).order_by(Property.created_at.desc()).limit(limit)
        
        return query.all()
    
    def get_properties_for_refresh(self, db: Session, limit: int = None) -> List[Property]:
        """
        Get properties that need translation refresh.
        
        Properties where multilingual content is older than 30 days.
        """
        limit = limit or self.batch_size
        
        # For now, we'll use created_at as proxy for when multilingual was last updated
        # In a full implementation, you'd want a separate timestamp for multilingual updates
        cutoff_date = datetime.now() - timedelta(days=30)
        
        query = db.query(Property).filter(
            and_(
                Property.is_available == True,
                Property.listing_type == 'rent',
                or_(
                    Property.title_en.isnot(None),
                    Property.title_ru.isnot(None)
                ),
                Property.created_at < cutoff_date
            )
        ).order_by(Property.created_at.asc()).limit(limit)
        
        return query.all()
    
    async def process_property_batch(self, properties: List[Property]) -> None:
        """Process a batch of properties for multilingual content."""
        if not properties:
            return
        
        self.logger.info(f"🌍 Processing batch of {len(properties)} properties for multilingual content")
        
        for property_obj in properties:
            try:
                await self.process_single_property(property_obj)
                self.stats.successful += 1
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process property {property_obj.external_id}: {e}")
                self.stats.failed += 1
            
            finally:
                self.stats.processed += 1
            
            # Small delay between properties to be respectful
            await asyncio.sleep(0.1)
    
    async def process_single_property(self, property_obj: Property) -> None:
        """Process a single property for multilingual content."""
        try:
            # Convert database property to PropertyData object
            property_data = self._convert_to_property_data(property_obj)
            
            self.logger.info(f"🔄 Processing multilingual content for property {property_data.external_id}")
            
            # Process multilingual content
            await self.multilingual_processor.process_multilingual_content(
                self.session, property_data
            )
            
            # Check if we got any new content
            has_new_content = False
            
            if property_data.title_en and property_data.title_en != property_obj.title_en:
                has_new_content = True
                self.logger.info(f"📝 Got new English title for property {property_data.external_id}")
                
            if property_data.title_ru and property_data.title_ru != property_obj.title_ru:
                has_new_content = True
                self.logger.info(f"📝 Got new Russian title for property {property_data.external_id}")
                
            if property_data.description_en and property_data.description_en != property_obj.description_en:
                has_new_content = True
                self.logger.info(f"📝 Got new English description for property {property_data.external_id}")
                
            if property_data.description_ru and property_data.description_ru != property_obj.description_ru:
                has_new_content = True
                self.logger.info(f"📝 Got new Russian description for property {property_data.external_id}")
            
            if has_new_content:
                # Update database with new multilingual content
                self._update_property_multilingual_content(property_obj, property_data)
                self.logger.info(f"✅ Successfully processed multilingual content for property {property_data.external_id}")
            else:
                self.logger.info(f"ℹ️ No new multilingual content found for property {property_data.external_id}")
                self.stats.skipped += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error processing property {property_obj.external_id}: {e}")
            raise
    
    def _convert_to_property_data(self, property_obj: Property) -> PropertyData:
        """Convert database Property object to PropertyData object."""
        return PropertyData(
            external_id=property_obj.external_id,
            title=property_obj.title or '',
            description=property_obj.description or '',
            title_en=property_obj.title_en,
            title_ru=property_obj.title_ru,
            description_en=property_obj.description_en,
            description_ru=property_obj.description_ru
        )
    
    def _update_property_multilingual_content(self, property_obj: Property, property_data: PropertyData) -> None:
        """Update database property with new multilingual content."""
        with SessionLocal() as db:
            try:
                # Update the property object
                if property_data.title_en and property_data.title_en != property_obj.title_en:
                    property_obj.title_en = property_data.title_en
                    self.logger.info(f"📝 Updated English title for property {property_obj.external_id}")
                
                if property_data.title_ru and property_data.title_ru != property_obj.title_ru:
                    property_obj.title_ru = property_data.title_ru
                    self.logger.info(f"📝 Updated Russian title for property {property_obj.external_id}")
                
                if property_data.description_en and property_data.description_en != property_obj.description_en:
                    property_obj.description_en = property_data.description_en
                    self.logger.info(f"📝 Updated English description for property {property_obj.external_id}")
                
                if property_data.description_ru and property_data.description_ru != property_obj.description_ru:
                    property_obj.description_ru = property_data.description_ru
                    self.logger.info(f"📝 Updated Russian description for property {property_obj.external_id}")
                
                # Merge and commit changes
                db.merge(property_obj)
                db.commit()
                
            except Exception as e:
                db.rollback()
                self.logger.error(f"❌ Failed to update property {property_obj.external_id} in database: {e}")
                raise
    
    async def run_batch_processing(self, mode: str = 'new') -> None:
        """Run batch processing for multilingual content."""
        self.logger.info(f"🚀 Starting multilingual batch processing in '{mode}' mode")
        
        with SessionLocal() as db:
            if mode == 'new':
                properties = self.get_properties_needing_translation(db)
                self.logger.info(f"📋 Found {len(properties)} properties needing translation")
            elif mode == 'refresh':
                properties = self.get_properties_for_refresh(db)
                self.logger.info(f"📋 Found {len(properties)} properties needing translation refresh")
            else:
                raise ValueError(f"Unknown processing mode: {mode}")
            
            if not properties:
                self.logger.info("ℹ️  No properties found for multilingual processing")
                return
            
            await self.process_property_batch(properties)
    
    async def run_continuous_processing(self, check_interval: int = 300) -> None:
        """Run continuous processing, checking for new properties periodically."""
        self.logger.info(f"🔄 Starting continuous multilingual processing (check interval: {check_interval}s)")
        
        while self.running:
            try:
                # Process new properties
                await self.run_batch_processing(mode='new')
                
                # Every 10th cycle, also refresh old properties
                if (self.stats.processed // self.batch_size) % 10 == 0:
                    await self.run_batch_processing(mode='refresh')
                
                self._log_stats()
                
                # Wait before next check
                self.logger.info(f"⏳ Waiting {check_interval} seconds before next check...")
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Received interrupt signal, stopping...")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"❌ Error in continuous processing: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)
    
    def _log_stats(self) -> None:
        """Log processing statistics."""
        elapsed = self.stats.get_elapsed_time()
        rate = self.stats.get_processing_rate()
        
        self.logger.info(f"📊 Processing stats:")
        self.logger.info(f"   - Processed: {self.stats.processed}")
        self.logger.info(f"   - Successful: {self.stats.successful}")
        self.logger.info(f"   - Failed: {self.stats.failed}")
        self.logger.info(f"   - Skipped: {self.stats.skipped}")
        self.logger.info(f"   - Elapsed time: {elapsed:.1f}s")
        self.logger.info(f"   - Processing rate: {rate:.2f} properties/second")


async def main():
    """Main entry point for the multilingual worker."""
    parser = argparse.ArgumentParser(description='Multilingual content processor for property data')
    parser.add_argument('--config-file', type=str, help='Path to configuration file')
    parser.add_argument('--batch-size', type=int, default=10, help='Number of properties to process in each batch')
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode')
    parser.add_argument('--mode', choices=['new', 'refresh'], default='new', 
                       help='Processing mode: new (unprocessed properties) or refresh (old translations)')
    parser.add_argument('--check-interval', type=int, default=300, 
                       help='Check interval in seconds for continuous mode')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config_file:
        config = ScrapingConfig.from_yaml(args.config_file)
    else:
        # Use environment variables and defaults
        config = ScrapingConfig()
    
    # Ensure multilingual processing is enabled
    config.concurrent_languages = True
    
    print(f"🌍 Multilingual Content Processor")
    print(f"   - Batch size: {args.batch_size}")
    print(f"   - Mode: {args.mode}")
    print(f"   - Continuous: {args.continuous}")
    if args.continuous:
        print(f"   - Check interval: {args.check_interval}s")
    print()
    
    # Create and run worker
    worker = MultilingualWorker(config, batch_size=args.batch_size)
    
    try:
        async with worker:
            if args.continuous:
                await worker.run_continuous_processing(args.check_interval)
            else:
                await worker.run_batch_processing(args.mode)
        
        # Final stats
        worker._log_stats()
        
    except KeyboardInterrupt:
        print("\n🛑 Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
