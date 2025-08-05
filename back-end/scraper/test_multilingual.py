#!/usr/bin/env python3
"""
Test script for multilingual processing.

This script tests the multilingual worker by processing a specific property ID.
"""

import asyncio
import sys
import os
import logging

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


async def test_single_property(property_id: str):
    """Test multilingual processing for a single property."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('MultilingualTest')
    
    # Create config
    config = ScrapingConfig()
    
    # Get property from database
    with SessionLocal() as db:
        property_obj = db.query(Property).filter(Property.external_id == property_id).first()
        if not property_obj:
            logger.error(f"Property {property_id} not found in database")
            return False
        
        logger.info(f"Found property: {property_obj.title}")
        logger.info(f"Current English title: {property_obj.title_en}")
        logger.info(f"Current Russian title: {property_obj.title_ru}")
        logger.info(f"Current English description: {property_obj.description_en and property_obj.description_en[:100]}")
        logger.info(f"Current Russian description: {property_obj.description_ru and property_obj.description_ru[:100]}")
    
    # Create worker and process
    worker = MultilingualWorker(config, batch_size=1)
    
    async with worker:
        try:
            await worker.process_single_property(property_obj)
            logger.info("✅ Processing completed successfully")
            
            # Check results
            with SessionLocal() as db:
                updated_property = db.query(Property).filter(Property.external_id == property_id).first()
                logger.info(f"Updated English title: {updated_property.title_en}")
                logger.info(f"Updated Russian title: {updated_property.title_ru}")
                logger.info(f"Updated English description: {updated_property.description_en and updated_property.description_en[:100]}")
                logger.info(f"Updated Russian description: {updated_property.description_ru and updated_property.description_ru[:100]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Processing failed: {e}")
            return False


async def main():
    """Main test function."""
    # Test with the property ID you mentioned
    property_id = "20246666"
    
    print(f"🧪 Testing multilingual processing for property {property_id}")
    success = await test_single_property(property_id)
    
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Allow specifying property ID as command line argument
        property_id = sys.argv[1]
        asyncio.run(test_single_property(property_id))
    else:
        asyncio.run(main())
