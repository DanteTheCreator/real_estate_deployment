#!/usr/bin/env python3
"""
Debug the multilingual configuration.
"""
import asyncio
import logging
import sys
import os

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.append('/app')

from scraper.core.config import ScrapingConfig
from scraper.processors.multilingual_processor import MultilingualProcessor
from scraper.models.property_data import PropertyData

async def debug_config():
    """Debug the multilingual configuration."""
    print("🔍 Debugging multilingual configuration...")
    
    # Create config
    config = ScrapingConfig()
    print(f"   concurrent_languages: {config.concurrent_languages}")
    print(f"   languages: {config.languages}")
    
    # Create processor
    processor = MultilingualProcessor(config)
    print(f"   is_multilingual_enabled(): {processor.is_multilingual_enabled()}")
    print(f"   supported_languages: {processor.get_supported_languages()}")
    
    # Create test property data
    property_data = PropertyData()
    property_data.external_id = "20246666"
    property_data.title = "იყიდება 2 ოთახიანი ბინა ბაგებში"
    property_data.description = "Beautiful apartment with great view"
    
    print(f"\n🔍 Testing multilingual processing...")
    print(f"   Property ID: {property_data.external_id}")
    print(f"   Title: {property_data.title}")
    
    # Test with a mock session
    import aiohttp
    async with aiohttp.ClientSession() as session:
        await processor.process_multilingual_content(session, property_data)
    
    print(f"\n📊 Results after processing:")
    print(f"   EN Title: {property_data.title_en}")
    print(f"   RU Title: {property_data.title_ru}")
    print(f"   EN Desc: {property_data.description_en}")
    print(f"   RU Desc: {property_data.description_ru}")

if __name__ == "__main__":
    asyncio.run(debug_config())
