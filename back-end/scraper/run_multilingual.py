#!/usr/bin/env python3
"""
Run multilingual worker in batch mode.

This script processes all properties that need multilingual content.
"""

import asyncio
import sys
import os
import logging
import argparse

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import Property, SessionLocal
    from scraper.core.config import ScrapingConfig
    from scraper.multilingual_worker import MultilingualWorker
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)


async def run_multilingual_batch(batch_size: int = 10, max_properties: int = None):
    """Run multilingual processing in batch mode."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('MultilingualBatch')
    
    # Create config
    config = ScrapingConfig()
    
    # Check how many properties need processing
    with SessionLocal() as db:
        total_needing_translation = len(MultilingualWorker(config).get_properties_needing_translation(db, limit=10000))
        logger.info(f"📊 Found {total_needing_translation} properties needing multilingual processing")
        
        if total_needing_translation == 0:
            logger.info("🎉 All properties already have multilingual content!")
            return
    
    # Create worker and process
    worker = MultilingualWorker(config, batch_size=batch_size)
    
    async with worker:
        processed_count = 0
        
        while True:
            # Get batch of properties
            with SessionLocal() as db:
                properties = worker.get_properties_needing_translation(db, limit=batch_size)
                
                if not properties:
                    logger.info("✅ No more properties need multilingual processing")
                    break
                
                if max_properties and processed_count >= max_properties:
                    logger.info(f"🛑 Reached maximum property limit ({max_properties})")
                    break
            
            logger.info(f"🔄 Processing batch of {len(properties)} properties...")
            
            try:
                await worker.process_property_batch(properties)
                processed_count += len(properties)
                
                logger.info(f"📈 Progress: {processed_count} properties processed")
                logger.info(f"📊 Success rate: {worker.stats.successful}/{worker.stats.processed} ({worker.stats.successful/worker.stats.processed*100:.1f}%)")
                
                # Small delay between batches
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"❌ Batch processing failed: {e}")
                break
        
        # Final statistics
        logger.info(f"🏁 Final Statistics:")
        logger.info(f"   📝 Total processed: {worker.stats.processed}")
        logger.info(f"   ✅ Successful: {worker.stats.successful}")
        logger.info(f"   ❌ Failed: {worker.stats.failed}")
        logger.info(f"   ⏭️ Skipped: {worker.stats.skipped}")
        logger.info(f"   ⏱️ Processing rate: {worker.stats.get_processing_rate():.2f} properties/second")


def main():
    """Main function with command line arguments."""
    parser = argparse.ArgumentParser(description='Run multilingual worker in batch mode')
    parser.add_argument('--batch-size', type=int, default=5, help='Number of properties to process in each batch')
    parser.add_argument('--max-properties', type=int, help='Maximum number of properties to process (optional)')
    parser.add_argument('--test-single', type=str, help='Test with a single property ID')
    
    args = parser.parse_args()
    
    if args.test_single:
        # Test single property
        from test_multilingual import test_single_property
        asyncio.run(test_single_property(args.test_single))
    else:
        # Run batch processing
        asyncio.run(run_multilingual_batch(args.batch_size, args.max_properties))


if __name__ == "__main__":
    main()
