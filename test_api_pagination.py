#!/usr/bin/env python3
"""
Test script to verify API pagination is working correctly.
"""

import requests
import json
from typing import Dict, Set

def test_api_pagination():
    """Test the MyHome.ge API pagination."""
    base_url = "https://api-statements.tnet.ge/v1/statements"
    
    # Proper headers as used by the scraper
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ka-GE,ka;q=0.9,en;q=0.8,ru;q=0.7',
        'global-authorization': '',
        'locale': 'ka',
        'origin': 'https://www.myhome.ge',
        'referer': 'https://www.myhome.ge/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'x-website-key': 'myhome'
    }
    
    # Test parameters
    params_base = {
        'currency_id': 1,
        'deal_types': '1,2,3,7',
        'real_estate_types': '2,1,3,4,5,6',
        'per_page': 1000  # Start with smaller page for testing
    }
    
    seen_ids = set()
    unique_ids_per_page = []
    
    print("🧪 Testing API pagination...")
    
    for page in range(1, 6):  # Test first 5 pages
        params = params_base.copy()
        params['page'] = page
        
        print(f"\n📄 Testing page {page}...")
        print(f"Request URL: {base_url}")
        print(f"Params: {params}")
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') and data.get('data') and data['data'].get('data'):
                properties = data['data']['data']
                print(f"✅ Page {page}: Found {len(properties)} properties")
                
                # Check for unique IDs
                page_ids = set()
                for prop in properties:
                    prop_id = prop.get('id')
                    if prop_id:
                        page_ids.add(str(prop_id))
                
                # Check overlaps with previous pages
                overlaps = page_ids.intersection(seen_ids)
                unique_in_page = len(page_ids - seen_ids)
                
                print(f"   📊 IDs in page: {len(page_ids)}")
                print(f"   🆕 Unique IDs: {unique_in_page}")
                print(f"   🔄 Overlapping IDs: {len(overlaps)}")
                
                if overlaps:
                    print(f"   ⚠️  Overlapping IDs: {list(overlaps)[:5]}...")
                
                unique_ids_per_page.append(unique_in_page)
                seen_ids.update(page_ids)
                
                # Show first and last property IDs
                if properties:
                    first_id = properties[0].get('id', 'unknown')
                    last_id = properties[-1].get('id', 'unknown')
                    print(f"   📋 ID range: {first_id} to {last_id}")
                
                # If no unique properties, pagination might be broken
                if unique_in_page == 0:
                    print(f"   ❌ No unique properties on page {page} - pagination issue!")
                    break
                    
            else:
                print(f"❌ Page {page}: No data in response")
                print(f"Response: {json.dumps(data, indent=2)[:500]}...")
                break
                
        except Exception as e:
            print(f"❌ Error on page {page}: {e}")
            break
    
    print(f"\n📈 Summary:")
    print(f"Total unique properties found: {len(seen_ids)}")
    print(f"Unique properties per page: {unique_ids_per_page}")
    
    # Check if pagination is working
    if len(unique_ids_per_page) > 1:
        decreasing = all(unique_ids_per_page[i] >= unique_ids_per_page[i+1] 
                        for i in range(len(unique_ids_per_page)-1))
        if decreasing:
            print("✅ Pagination appears to be working (unique properties decrease over pages)")
        else:
            print("⚠️  Pagination might have issues (unique properties don't decrease consistently)")
    
    return len(seen_ids), unique_ids_per_page

if __name__ == "__main__":
    test_api_pagination()
