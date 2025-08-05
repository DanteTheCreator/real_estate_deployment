#!/usr/bin/env python3
"""
Debug test script with detailed logging.
"""
import asyncio
import logging
import sys
import os

# Setup very detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Property, SessionLocal
from scraper.core.config import ScrapingConfig
from scraper.multilingual_worker import MultilingualWorker

async def debug_multilingual_processing():
    """Debug multilingual processing step by step."""
    property_id = "20246666"
    
    # Create config
    config = ScrapingConfig()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the property
        property_obj = db.query(Property).filter(
            Property.external_id == property_id
        ).first()
        
        if not property_obj:
            print(f"❌ Property {property_id} not found")
            return
        
        print(f"✅ Found property: {property_obj.title}")
        print(f"   External ID: {property_obj.external_id}")
        print(f"   Before - EN title: {property_obj.title_en}")
        print(f"   Before - RU title: {property_obj.title_ru}")
        print(f"   Before - EN desc: {property_obj.description_en}")
        print(f"   Before - RU desc: {property_obj.description_ru}")
        
        # Create and test the worker
        worker = MultilingualWorker(config, batch_size=1)
        
        print(f"\n🔍 Step 1: Converting to PropertyData...")
        property_data = worker._convert_to_property_data(property_obj)
        print(f"   PropertyData title: {property_data.title}")
        print(f"   PropertyData external_id: {property_data.external_id}")
        
        print(f"\n🔍 Step 2: Processing multilingual content...")
        async with worker:
            # Process the multilingual content directly
            await worker.multilingual_processor.process_multilingual_content(
                worker.session, property_data
            )
        
        print(f"\n🔍 Step 3: After processing - checking PropertyData...")
        print(f"   PropertyData EN title: {property_data.title_en}")
        print(f"   PropertyData RU title: {property_data.title_ru}")
        print(f"   PropertyData EN desc: {property_data.description_en}")
        print(f"   PropertyData RU desc: {property_data.description_ru}")
        
        print(f"\n🔍 Step 4: Checking if content changed...")
        has_changes = False
        
        if property_data.title_en and property_data.title_en != property_obj.title_en:
            print(f"   ✅ English title changed: '{property_obj.title_en}' -> '{property_data.title_en}'")
            has_changes = True
            
        if property_data.title_ru and property_data.title_ru != property_obj.title_ru:
            print(f"   ✅ Russian title changed: '{property_obj.title_ru}' -> '{property_data.title_ru}'")
            has_changes = True
            
        if property_data.description_en and property_data.description_en != property_obj.description_en:
            print(f"   ✅ English description changed")
            has_changes = True
            
        if property_data.description_ru and property_data.description_ru != property_obj.description_ru:
            print(f"   ✅ Russian description changed")
            has_changes = True
        
        if has_changes:
            print(f"\n🔍 Step 5: Updating database...")
            worker._update_property_multilingual_content(property_obj, property_data)
            
            # Refresh to see changes
            db.refresh(property_obj)
            
            print(f"\n📊 Final Results:")
            print(f"   Georgian title: {property_obj.title}")
            print(f"   English title: {property_obj.title_en}")
            print(f"   Russian title: {property_obj.title_ru}")
            print(f"   English desc: {property_obj.description_en[:100] if property_obj.description_en else 'None'}...")
            print(f"   Russian desc: {property_obj.description_ru[:100] if property_obj.description_ru else 'None'}...")
        else:
            print(f"   ℹ️ No changes detected")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug_multilingual_processing())
