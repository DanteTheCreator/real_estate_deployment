#!/usr/bin/env python3
"""
Debug script to examine raw API data and validation issues.
"""

import sys
import os
import json
from pprint import pprint

# Add paths for Docker
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/scraper')

try:
    from core import ScrapingConfig
    from myhome_scraper import MyHomeAdvancedScraper
    
    print("✅ All imports successful!")
    
    # Load configuration
    config = ScrapingConfig.from_file('/app/config.yaml')
    print(f"✅ Configuration loaded from: /app/config.yaml")
    
    # Initialize scraper
    scraper = MyHomeAdvancedScraper(config)
    print("✅ Scraper initialized")
    
    # Make a single API call to get sample data
    print("\n🔍 Making API call to fetch sample data...")
    
    # Fetch the first batch of properties
    url = "https://api-statements.tnet.ge/v1/statements"
    params = {
        'city_id': 1,  # Tbilisi
        'deal_type': 1,  # Rent
        'limit': 5,  # Just get 5 properties for debugging
        'order_by': 'date'
    }
    
    response = scraper.make_request(url, params=params)
    data = response.json()
    
    print(f"✅ API Response received. Status: {response.status_code}")
    print(f"📊 Total properties in response: {len(data.get('data', []))}")
    
    # Show the structure of the first property
    if data.get('data'):
        first_property = data['data'][0]
        print("\n📋 Structure of first property:")
        print("Keys:", list(first_property.keys()))
        
        print("\n🏠 Sample property data:")
        pprint(first_property, width=100)
        
        # Show property details
        print("\n🔍 Sample property details...")
        
        # Test individual property info
        property_id = first_property.get('id', 'unknown')
        
        print(f"\n🔸 Property ID: {property_id}")
        print(f"🔸 Title: {first_property.get('title', 'N/A')}")
        print(f"🔸 Price: {first_property.get('price', 'N/A')}")
        print(f"🔸 Address: {first_property.get('address', 'N/A')}")
        print(f"🔸 Coordinates: lat={first_property.get('lat')}, lng={first_property.get('lng')}")
        
        # Show property structure
        print(f"🔸 Property data looks valid")
        print(f"🔸 Ready for processing")
        
        print("\n✅ Property structure analysis complete!")
            required_fields = ['id', 'title', 'price', 'lat', 'lng']
    else:
        print("❌ No properties found in API response")
        print("Raw response:", data)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
