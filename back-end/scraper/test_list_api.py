#!/usr/bin/env python3
"""
Test the main API endpoint to verify auth works.
"""
import asyncio
import aiohttp
import sys
import os

sys.path.append('/app')

async def test_list_api():
    """Test the main list API to verify auth works."""
    
    # Test the list endpoint that we know works from the main scraper
    list_url = "https://api-statements.tnet.ge/v1/statements"
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,ka;q=0.8,und;q=0.7',
        'global-authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ2IjoxLCJpYXQiOjE3NTQzODU3NjksImV4cGlyZXNfYXQiOjE3NTQzODY0MjksImRhdGEiOnsidXNlcl9pZCI6NTEwNTQzMywidXNlcm5hbWUiOiJrYXhhbWlxZWxhZHplQGdtYWlsLmNvbSIsInNlc3Npb25faWQiOiIzYzA2NjE4YjU0NGMyMTI4MTBkN2NhYjRhMDQ1Mzk5MDFlYThmZDljNWEwN2FhMWE3ZmI4NTdhMTdlOWVjNGZiIiwibGl2b191c2VyX2lkIjpudWxsLCJzd29vcF91c2VyX2lkIjozODQxNjAsInRrdF91c2VyX2lkIjpudWxsLCJnZW5kZXJfaWQiOjEsImJpcnRoX3llYXIiOjE5NzgsImJpcnRoX2RhdGUiOiIxOTc4LTA4LTAxIiwicGhvbmUiOiI1OTk3MzgwMjMiLCJ1c2VyX25hbWUiOiJrYXhhIiwidXNlcl9zdXJuYW1lIjoibWlxZWxhZHplIiwidHlwZV9pZCI6MH19.DES3OMjLem3W0em42vnxoSEYOAq4jLEAjjjixvRyqDJT0bQHd30wFqqjSrSfGH9iLZkMp0gtrXiVFJGV_RlWTlTvwfQCVzZM4H58dS-nescI2DZy4CZdTF9u45nWtgxXxhnz9Kk0gbHaVtqXHu1rUnxLJQoGc9g1k0JSH_Y9xDPoBbsNmqivRu5E7BXkh2Q6eXXL6BuCxWRxaNeD7pJ8dQmrEt4HVOoqTvMD_TiHE-dvgf5RqQRK7q3JOd4f-niXIKwjgn1JCCU3WUPUhvjEiCR_lV-OmyB_3IHCxoDcNr7sT48fBvYYsYLOhrjZVbUNVdmPO0JZFUIskq_6vWG3dw',
        'locale': 'en',
        'origin': 'https://www.myhome.ge',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    # Parameters that work from the main scraper
    params = {
        'currency_id': 1,
        'deal_types': '1,2,3,7',
        'real_estate_types': '2,1,3,4,5,6',
        'page': 1,
        'per_page': 5  # Just get a few properties
    }
    
    print(f"🔍 Testing list API to verify auth works")
    print(f"   URL: {list_url}")
    print(f"   Params: {params}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(list_url, headers=headers, params=params, timeout=10) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"   Success! Got response with result: {data.get('result')}")
                        
                        if data.get('result') and data.get('data'):
                            properties = data['data'].get('data', [])
                            print(f"   Found {len(properties)} properties")
                            
                            if properties:
                                first_prop = properties[0]
                                print(f"   First property ID: {first_prop.get('id')}")
                                print(f"   Property has title: {first_prop.get('dynamic_title', 'NO TITLE')[:50]}...")
                                
                                # Now test accessing this specific property
                                property_id = first_prop.get('id')
                                if property_id:
                                    await test_single_property(session, property_id, headers)
                        
                    except Exception as e:
                        text = await response.text()
                        print(f"   Failed to parse JSON: {e}")
                        print(f"   Response text: {text[:200]}")
                        
                else:
                    text = await response.text()
                    print(f"   Error response: {text}")
                    
        except Exception as e:
            print(f"   Request failed: {e}")

async def test_single_property(session, property_id, headers):
    """Test accessing a single property."""
    detail_url = f"https://api-statements.tnet.ge/v1/statements/{property_id}"
    
    print(f"\n🔍 Testing single property access:")
    print(f"   Property ID: {property_id}")
    print(f"   URL: {detail_url}")
    
    try:
        async with session.get(detail_url, headers=headers, timeout=10) as response:
            print(f"   Status: {response.status}")
            
            if response.status == 200:
                try:
                    data = await response.json()
                    print(f"   Success! Property access works")
                    if data.get('result') and data.get('data'):
                        prop_data = data['data']
                        title = prop_data.get('dynamic_title', 'NO TITLE')
                        print(f"   Property title: {title[:50]}...")
                    else:
                        print("   No property data in response")
                        
                except Exception as e:
                    text = await response.text()
                    print(f"   Failed to parse JSON: {e}")
                    print(f"   Response: {text[:200]}")
                    
            else:
                text = await response.text()
                print(f"   Error: {text}")
                
    except Exception as e:
        print(f"   Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_list_api())
