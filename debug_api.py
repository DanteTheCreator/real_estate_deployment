#!/usr/bin/env python3
import json
import requests

# Simple script to fetch sample API data from MyHome.ge
def fetch_sample_data():
    url = "https://api-statements.tnet.ge/v1/statements"
    
    params = {
        'statement_types': 4,  # Rentals
        'cities[]': 1,         # Tbilisi
        'limit': 2             # Just 2 properties for debugging
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            print("Sample API Response Properties:")
            print("=" * 50)
            for i, prop in enumerate(data['data'][:2]):
                print(f"Property {i+1}:")
                print(json.dumps(prop, indent=2, ensure_ascii=False))
                print("-" * 30)
        else:
            print("No data found in response")
            print("Full response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_sample_data()
