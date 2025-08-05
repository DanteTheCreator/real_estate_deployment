#!/usr/bin/env python3
"""
Simple test for multilingual processor.
"""
import logging
import asyncio
import aiohttp
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

async def test_direct_api():
    """Test direct API call to see if it works."""
    property_id = "20246666"
    language = "en"
    
    # Create the URL directly - using correct MyHome.ge API structure
    detail_url = f"https://api-statements.tnet.ge/v1/statements/{property_id}"
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': f'{language}-US,{language};q=0.9,ka;q=0.8,und;q=0.7',
        'global-authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ2IjoxLCJpYXQiOjE3NTQzODU3NjksImV4cGlyZXNfYXQiOjE3NTQzODY0MjksImRhdGEiOnsidXNlcl9pZCI6NTEwNTQzMywidXNlcm5hbWUiOiJrYXhhbWlxZWxhZHplQGdtYWlsLmNvbSIsInNlc3Npb25faWQiOiIzYzA2NjE4YjU0NGMyMTI4MTBkN2NhYjRhMDQ1Mzk5MDFlYThmZDljNWEwN2FhMWE3ZmI4NTdhMTdlOWVjNGZiIiwibGl2b191c2VyX2lkIjpudWxsLCJzd29vcF91c2VyX2lkIjozODQxNjAsInRrdF91c2VyX2lkIjpudWxsLCJnZW5kZXJfaWQiOjEsImJpcnRoX3llYXIiOjE5NzgsImJpcnRoX2RhdGUiOiIxOTc4LTA4LTAxIiwicGhvbmUiOiI1OTk3MzgwMjMiLCJ1c2VyX25hbWUiOiJrYXhhIiwidXNlcl9zdXJuYW1lIjoibWlxZWxhZHplIiwidHlwZV9pZCI6MH19.DES3OMjLem3W0em42vnxoSEYOAq4jLEAjjjixvRyqDJT0bQHd30wFqqjSrSfGH9iLZkMp0gtrXiVFJGV_RlWTlTvwfQCVzZM4H58dS-nescI2DZy4CZdTF9u45nWtgxXxhnz9Kk0gbHaVtqXHu1rUnxLJQoGc9g1k0JSH_Y9xDPoBbsNmqivRu5E7BXkh2Q6eXXL6BuCxWRxaNeD7pJ8dQmrEt4HVOoqTvMD_TiHE-dvgf5RqQRK7q3JOd4f-niXIKwjgn1JCCU3WUPUhvjEiCR_lV-OmyB_3IHCxoDcNr7sT48fBvYYsYLOhrjZVbUNVdmPO0JZFUIskq_6vWG3dw',
        'locale': language,
        'origin': 'https://www.myhome.ge',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Testing direct API call to: {detail_url}")
    print(f"   Language: {language}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(detail_url, headers=headers, timeout=10) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"   Response type: {type(data)}")
                        print(f"   Response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
                        
                        if isinstance(data, dict):
                            if 'data' in data:
                                prop_data = data['data']
                                print(f"   Property data keys: {prop_data.keys() if isinstance(prop_data, dict) else 'Not a dict'}")
                                
                                title = (prop_data.get('dynamic_title') or 
                                        prop_data.get('title') or 
                                        prop_data.get('name'))
                                print(f"   Title found: {title}")
                                
                            else:
                                print("   No 'data' key in response")
                        
                    except Exception as e:
                        text = await response.text()
                        print(f"   Failed to parse JSON: {e}")
                        print(f"   Response text (first 200 chars): {text[:200]}")
                        
                else:
                    text = await response.text()
                    print(f"   Error response: {text[:200]}")
                    
        except Exception as e:
            print(f"   Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_api())
