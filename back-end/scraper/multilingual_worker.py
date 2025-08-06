#!/usr/bin/env python3
"""
Multilingual Content Processor Worker
Processes property listings to generate multilingual content
"""

import os
import sys
import time
import argparse
import logging
from typing import List, Optional
from datetime import datetime, timedelta

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, Property
from sqlalchemy.orm import Session
from processors.multilingual_processor import MultilingualProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/worker_logs/multilingual_worker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MultilingualWorker:
    """Worker for processing multilingual content"""
    
    def __init__(self, batch_size: int = 10, check_interval: int = 300):
        self.batch_size = batch_size
        self.check_interval = check_interval
        self.processor = MultilingualProcessor()
        
    def get_unprocessed_properties(self, db: Session, limit: int = None) -> List[Property]:
        """Get properties that need multilingual processing"""
        query = db.query(Property).filter(
            Property.is_available == True,
            Property.multilingual_processed == False
        )
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def process_property_batch(self, properties: List[Property], db: Session) -> int:
        """Process a batch of properties for multilingual content"""
        processed_count = 0
        
        for property_item in properties:
            try:
                logger.info(f"Processing property {property_item.id}: {property_item.title}")
                
                # Process multilingual content
                success = self.processor.process_property(property_item, db)
                
                if success:
                    # Mark as processed
                    property_item.multilingual_processed = True
                    property_item.multilingual_processed_at = datetime.utcnow()
                    processed_count += 1
                    logger.info(f"✅ Successfully processed property {property_item.id}")
                else:
                    logger.error(f"❌ Failed to process property {property_item.id}")
                    
            except Exception as e:
                logger.error(f"Error processing property {property_item.id}: {str(e)}")
                continue
        
        try:
            db.commit()
            logger.info(f"Committed {processed_count} processed properties to database")
        except Exception as e:
            logger.error(f"Error committing to database: {str(e)}")
            db.rollback()
            processed_count = 0
            
        return processed_count
    
    def run_single_batch(self) -> int:
        """Run a single processing batch"""
        db = next(get_db())
        
        try:
            properties = self.get_unprocessed_properties(db, self.batch_size)
            
            if not properties:
                logger.info("No unprocessed properties found")
                return 0
            
            logger.info(f"Found {len(properties)} properties to process")
            return self.process_property_batch(properties, db)
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return 0
        finally:
            db.close()
    
    def run_continuous(self):
        """Run continuous processing"""
        logger.info(f"Starting continuous multilingual worker")
        logger.info(f"Batch size: {self.batch_size}, Check interval: {self.check_interval}s")
        
        while True:
            try:
                start_time = datetime.now()
                processed = self.run_single_batch()
                
                if processed > 0:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Processed {processed} properties in {duration:.2f}s")
                
                logger.info(f"Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Multilingual Content Processor Worker')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of properties to process per batch')
    parser.add_argument('--check-interval', type=int, default=300,
                       help='Interval between checks in seconds')
    parser.add_argument('--continuous', action='store_true',
                       help='Run in continuous mode')
    parser.add_argument('--single-batch', action='store_true',
                       help='Process a single batch and exit')
    
    args = parser.parse_args()
    
    # Get configuration from environment
    batch_size = int(os.getenv('BATCH_SIZE', args.batch_size))
    check_interval = int(os.getenv('CHECK_INTERVAL', args.check_interval))
    
    worker = MultilingualWorker(batch_size, check_interval)
    
    if args.continuous:
        worker.run_continuous()
    elif args.single_batch:
        processed = worker.run_single_batch()
        logger.info(f"Single batch complete. Processed {processed} properties.")
    else:
        # Default to continuous mode
        worker.run_continuous()


if __name__ == "__main__":
    main()
