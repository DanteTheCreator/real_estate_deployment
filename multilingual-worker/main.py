#!/usr/bin/env python3
"""
Multilingual Content Worker - Standalone Service

A dedicated service for processing multilingual content for properties.
Fetches English and Russian translations from MyHome.ge API and updates
the database with multilingual content.

Author: Production Team
Version: 1.0.0
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import MultilingualConfig
from src.processors.multilingual_processor import MultilingualProcessor
from src.models.property_data import PropertyData
from src.services.database_service import DatabaseService


@dataclass
class ProcessingStats:
    """Statistics for multilingual processing."""
    processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return (self.successful / self.processed) * 100


class MultilingualWorker:
    """Standalone multilingual content processor."""
    
    def __init__(self, config: MultilingualConfig, batch_size: int = 10):
        """Initialize the multilingual worker."""
        self.config = config
        self.batch_size = batch_size
        self.stats = ProcessingStats()
        self.running = True
        self.session = None
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize services
        self.database_service = DatabaseService(config)
        self.multilingual_processor = MultilingualProcessor(config)
    
    async def __aenter__(self):
        """Async context manager entry."""
        import aiohttp
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        if self.database_service:
            await self.database_service.close()
    
    async def get_properties_needing_translation(self, limit: int = None) -> List[PropertyData]:
        """Get properties that need multilingual processing."""
        limit = limit or self.batch_size
        return await self.database_service.get_properties_for_multilingual_processing(limit)
    
    async def process_property_batch(self, properties: List[PropertyData]) -> None:
        """Process a batch of properties for multilingual content."""
        if not properties:
            return
        
        self.logger.info(f"🌍 Processing batch of {len(properties)} properties for multilingual content")
        
        for property_data in properties:
            try:
                await self.process_single_property_data(property_data)
                self.stats.successful += 1
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process property {property_data.external_id}: {e}")
                self.stats.failed += 1
            
            finally:
                self.stats.processed += 1
            
            # Small delay between properties
            await asyncio.sleep(0.1)
    
    async def process_single_property_data(self, property_data: PropertyData) -> None:
        """Process a single property for multilingual content."""
        try:
            self.logger.info(f"🔄 Processing multilingual content for property {property_data.external_id}")
            
            # Store original values to check for changes
            original_title_en = property_data.title_en
            original_title_ru = property_data.title_ru
            original_desc_en = property_data.description_en
            original_desc_ru = property_data.description_ru
            
            # Process multilingual content
            await self.multilingual_processor.process_multilingual_content(
                self.session, property_data
            )
            
            # Check if we got any new content
            has_new_content = False
            
            if property_data.title_en and property_data.title_en != original_title_en:
                has_new_content = True
                self.logger.info(f"📝 Got new English title for property {property_data.external_id}")
                
            if property_data.title_ru and property_data.title_ru != original_title_ru:
                has_new_content = True
                self.logger.info(f"📝 Got new Russian title for property {property_data.external_id}")
                
            if property_data.description_en and property_data.description_en != original_desc_en:
                has_new_content = True
                self.logger.info(f"📝 Got new English description for property {property_data.external_id}")
                
            if property_data.description_ru and property_data.description_ru != original_desc_ru:
                has_new_content = True
                self.logger.info(f"📝 Got new Russian description for property {property_data.external_id}")
            
            if has_new_content:
                # Update database with new multilingual content
                success = await self.database_service.update_property_multilingual_content(property_data)
                if success:
                    self.logger.info(f"✅ Successfully processed multilingual content for property {property_data.external_id}")
                else:
                    self.logger.error(f"❌ Failed to update database for property {property_data.external_id}")
                    raise Exception("Database update failed")
            else:
                self.logger.info(f"ℹ️ No new multilingual content found for property {property_data.external_id}")
                self.stats.skipped += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error processing property {property_data.external_id}: {e}")
            raise
    
    async def run_batch_processing(self, limit: int = None) -> None:
        """Run batch processing for multilingual content."""
        self.logger.info(f"🚀 Starting multilingual batch processing")
        self.stats.start_time = datetime.now()
        
        properties = await self.get_properties_needing_translation(limit)
        self.logger.info(f"📋 Found {len(properties)} properties needing translation")
        
        if not properties:
            self.logger.info("ℹ️  No properties found for multilingual processing")
            return
        
        await self.process_property_batch(properties)
        
        self.stats.end_time = datetime.now()
        self._log_final_stats()
    
    async def run_continuous_processing(self, check_interval: int = 300) -> None:
        """Run continuous processing, checking for new properties periodically."""
        self.logger.info(f"🔄 Starting continuous multilingual processing (check interval: {check_interval}s)")
        self.stats.start_time = datetime.now()
        
        while self.running:
            try:
                # Process new properties
                await self.run_batch_processing()
                
                # Wait before next check
                self.logger.info(f"😴 Waiting {check_interval} seconds before next check...")
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Received interrupt signal, stopping...")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"❌ Error in continuous processing: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
        
        self.stats.end_time = datetime.now()
        self._log_final_stats()
    
    def _log_final_stats(self) -> None:
        """Log final processing statistics."""
        self.logger.info("📊 Final Processing Statistics:")
        self.logger.info(f"   Total processed: {self.stats.processed}")
        self.logger.info(f"   Successful: {self.stats.successful}")
        self.logger.info(f"   Failed: {self.stats.failed}")
        self.logger.info(f"   Skipped: {self.stats.skipped}")
        self.logger.info(f"   Success rate: {self.stats.success_rate:.1f}%")
        self.logger.info(f"   Duration: {self.stats.duration_seconds:.1f} seconds")


async def main():
    """Main entry point for the multilingual worker."""
    parser = argparse.ArgumentParser(description='Multilingual Content Worker')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    parser.add_argument('--limit', type=int, help='Limit number of properties to process')
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode')
    parser.add_argument('--interval', type=int, default=300, help='Check interval for continuous mode (seconds)')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🌍 Starting Multilingual Content Worker")
    
    # Create configuration
    config = MultilingualConfig()
    
    # Create and run worker
    worker = MultilingualWorker(config, batch_size=args.batch_size)
    
    try:
        async with worker:
            if args.continuous:
                await worker.run_continuous_processing(args.interval)
            else:
                await worker.run_batch_processing(args.limit)
                
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    
    logger.info("✅ Multilingual worker finished")


if __name__ == "__main__":
    asyncio.run(main())
