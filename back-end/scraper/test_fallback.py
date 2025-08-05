#!/usr/bin/env python3
import asyncio
import aiohttp
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append('/app')

from scraper.core.config import ScrapingConfig
from scraper.processors.multilingual_processor import MultilingualProcessor
from scraper.models.property_data import PropertyData

async def test_fallback():
    """Test fallback translations directly."""
    config = ScrapingConfig()
    processor = MultilingualProcessor(config)
    
    # Create test property with Georgian text
    prop = PropertyData(external_id='20246666')
    prop.title = 'იყიდება 2 ოთახიანი ბინა ბაგებში'
    prop.description = 'ძალიან კარგი ბინა ცენტრში, ახალი რემონტი'
    
    print(f'Before processing:')
    print(f'  Title: {prop.title}')
    print(f'  EN Title: {prop.title_en}')
    print(f'  RU Title: {prop.title_ru}')
    
    # Test multilingual processing
    async with aiohttp.ClientSession() as session:
        await processor.process_multilingual_content(session, prop)
    
    print(f'\nAfter processing:')
    print(f'  EN Title: {prop.title_en}')
    print(f'  RU Title: {prop.title_ru}')
    print(f'  EN Desc: {prop.description_en}')
    print(f'  RU Desc: {prop.description_ru}')
    
    # Test fallback directly
    print(f'\nTesting fallback directly:')
    processor._apply_fallback_translations(prop)
    
    print(f'After fallback:')
    print(f'  EN Title: {prop.title_en}')
    print(f'  RU Title: {prop.title_ru}')

if __name__ == "__main__":
    asyncio.run(test_fallback())
