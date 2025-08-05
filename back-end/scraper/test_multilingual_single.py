#!/usr/bin/env python3
"""
Test script to validate multilingual worker with a specific property.
"""
import asyncio
import logging
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Property, SessionLocal
from scraper.core.config import ScrapingConfig

# Direct import to avoid circular dependency
from scraper.multilingual_worker import MultilingualWorker

# Setup logging  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_single_property():
    """Test multilingual processing for a specific property."""
    property_id = "20246666"  # The property ID from earlier
    
    # Create config
    config = ScrapingConfig()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the property in our database
        property_obj = db.query(Property).filter(
            Property.external_id == property_id
        ).first()
        
        if not property_obj:
            print(f"❌ Property {property_id} not found in database")
            # Let's see what properties we do have
            properties = db.query(Property).limit(5).all()
            print("\n📋 Available properties:")
            for prop in properties:
                print(f"  - ID: {prop.external_id}, Title: {prop.title[:50]}...")
            return
        
        print(f"✅ Found property: {property_obj.title}")
        print(f"   External ID: {property_obj.external_id}")
        print(f"   Current EN title: {property_obj.title_en}")
        print(f"   Current RU title: {property_obj.title_ru}")
        
        # Create multilingual worker
        worker = MultilingualWorker(config, batch_size=1)
        
        # Process the property
        print(f"\n🌍 Starting multilingual processing...")
        async with worker:
            await worker.process_single_property(property_obj)
        
        # Refresh and check results
        db.refresh(property_obj)
        
        print(f"\n📊 Results:")
        print(f"   Georgian title: {property_obj.title}")
        print(f"   English title: {property_obj.title_en}")
        print(f"   Russian title: {property_obj.title_ru}")
        print(f"   English desc: {property_obj.description_en[:100] if property_obj.description_en else 'None'}...")
        print(f"   Russian desc: {property_obj.description_ru[:100] if property_obj.description_ru else 'None'}...")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_single_property())
