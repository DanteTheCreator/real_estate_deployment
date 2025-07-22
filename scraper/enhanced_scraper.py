#!/usr/bin/env python3
"""
Enhanced Property Scraper with additional features and better deduplication logic
"""

import requests
import time
import json
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging
import argparse
import sys
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Property:
    """Enhanced data class to represent a property with key attributes for deduplication"""
    id: int
    address: str
    room: str
    bedroom: str
    area: int
    floor: int
    total_floors: int
    price_total: int
    user_type: str  # 'physical' for owner, 'agent' for agent
    deal_type_id: int
    real_estate_type_id: int
    city_name: str
    district_name: str
    urban_name: str
    lat: float
    lng: float
    last_updated: str
    user_title: str
    comment: str
    raw_data: dict
    
    @property
    def dedup_key(self) -> Tuple:
        """Create a key for deduplication based on address, rooms, area, and location"""
        # Normalize address for better matching
        normalized_address = self.address.lower().strip().replace('  ', ' ')
        
        return (
            normalized_address,
            self.room,
            self.bedroom,
            self.area,
            self.floor or 0,  # Handle None floors
            self.total_floors or 0,  # Handle None total_floors
            self.urban_name.lower().strip() if self.urban_name else '',
            # Round coordinates to 4 decimal places for approximate location matching
            round(self.lat, 4) if self.lat else 0,
            round(self.lng, 4) if self.lng else 0
        )
    
    @property
    def is_owner(self) -> bool:
        """Check if the listing is by owner (physical person)"""
        return self.user_type == 'physical'
    
    def to_dict(self) -> dict:
        """Convert to dictionary excluding raw_data for cleaner output"""
        data = asdict(self)
        data.pop('raw_data', None)  # Remove raw_data for cleaner output
        return data

class EnhancedPropertyScraper:
    def __init__(self, delay: float = 1.0, per_page: int = 100):
        self.base_url = "https://api-statements.tnet.ge/v1/statements"
        self.per_page = min(per_page, 100)  # API max is 100
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,ka;q=0.8,und;q=0.7',
            'global-authorization': '',
            'locale': 'ka',
            'origin': 'https://www.myhome.ge',
            'priority': 'u=1, i',
            'referer': 'https://www.myhome.ge/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-website-key': 'myhome',
        }
        self.properties: List[Property] = []
        self.request_delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_page(self, page: int, cities: str = '1', currency_id: str = '1') -> Optional[Dict]:
        """Fetch a single page of properties with retry logic"""
        params = {
            'page': str(page),
            'per_page': str(self.per_page),
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for page {page}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch page {page} after {max_retries} attempts")
                    return None
    
    def parse_property(self, property_data: Dict) -> Property:
        """Parse raw property data into Property object with enhanced error handling"""
        # Get price in the primary currency (currency_id 1 seems to be GEL)
        price_data = property_data.get('price', {})
        price_total = 0
        if '1' in price_data:
            price_total = price_data['1'].get('price_total', 0)
        elif price_data:
            # Fallback to any available price
            first_currency = list(price_data.keys())[0]
            price_total = price_data[first_currency].get('price_total', 0)
        
        # Get user type (physical = owner, agent = agent)
        user_type_data = property_data.get('user_type', {})
        user_type = user_type_data.get('type', 'unknown')
        
        return Property(
            id=property_data.get('id', 0),
            address=property_data.get('address', ''),
            room=str(property_data.get('room', '')),
            bedroom=str(property_data.get('bedroom', '')),
            area=property_data.get('area', 0) or 0,
            floor=property_data.get('floor') or 0,
            total_floors=property_data.get('total_floors') or 0,
            price_total=price_total,
            user_type=user_type,
            deal_type_id=property_data.get('deal_type_id', 0),
            real_estate_type_id=property_data.get('real_estate_type_id', 0),
            city_name=property_data.get('city_name', ''),
            district_name=property_data.get('district_name', ''),
            urban_name=property_data.get('urban_name', ''),
            lat=property_data.get('lat', 0.0) or 0.0,
            lng=property_data.get('lng', 0.0) or 0.0,
            last_updated=property_data.get('last_updated', ''),
            user_title=property_data.get('user_title', ''),
            comment=property_data.get('comment', ''),
            raw_data=property_data
        )
    
    def fetch_all_properties(self, max_pages: Optional[int] = None, cities: str = '1') -> List[Property]:
        """Fetch all properties from all pages with progress tracking"""
        page = 1
        all_properties = []
        empty_pages = 0
        max_empty_pages = 3  # Stop if we get 3 consecutive empty pages
        
        logger.info(f"Starting to fetch properties for cities: {cities}")
        if max_pages:
            logger.info(f"Limited to {max_pages} pages")
        
        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached maximum pages limit: {max_pages}")
                break
            
            if empty_pages >= max_empty_pages:
                logger.info(f"Stopping after {max_empty_pages} consecutive empty pages")
                break
                
            logger.info(f"Fetching page {page}...")
            data = self.fetch_page(page, cities=cities)
            
            if not data or not data.get('result'):
                logger.warning(f"Failed to fetch data for page {page}")
                empty_pages += 1
                page += 1
                continue
            
            properties_data = data.get('data', {}).get('data', [])
            
            if not properties_data:
                logger.info(f"No properties found on page {page}")
                empty_pages += 1
                page += 1
                continue
            
            # Reset empty pages counter
            empty_pages = 0
            
            # Parse properties from this page
            page_properties = []
            for prop_data in properties_data:
                try:
                    property_obj = self.parse_property(prop_data)
                    page_properties.append(property_obj)
                except Exception as e:
                    logger.error(f"Error parsing property {prop_data.get('id', 'unknown')}: {e}")
            
            all_properties.extend(page_properties)
            logger.info(f"Fetched {len(page_properties)} properties from page {page}. Total: {len(all_properties)} ({self.per_page} per page)")
            
            # Add delay between requests
            time.sleep(self.request_delay)
            page += 1
        
        logger.info(f"Finished fetching. Total properties: {len(all_properties)}")
        self.properties = all_properties
        return all_properties
    
    def deduplicate_properties(self, properties: List[Property], similarity_threshold: float = 0.9) -> List[Property]:
        """
        Enhanced deduplication with similarity checking and detailed logging
        """
        logger.info("Starting enhanced deduplication...")
        
        # Group properties by deduplication key
        property_groups = defaultdict(list)
        for prop in properties:
            property_groups[prop.dedup_key].append(prop)
        
        deduplicated = []
        duplicates_removed = 0
        duplicate_details = []
        
        for dedup_key, group_properties in property_groups.items():
            if len(group_properties) == 1:
                # No duplicates
                deduplicated.append(group_properties[0])
            else:
                # Handle duplicates
                duplicates_removed += len(group_properties) - 1
                
                # Sort by preference: owners first, then by price (descending)
                sorted_properties = sorted(
                    group_properties,
                    key=lambda p: (not p.is_owner, -p.price_total, p.id)  # Add ID for consistent sorting
                )
                
                best_property = sorted_properties[0]
                deduplicated.append(best_property)
                
                # Log detailed information about this duplicate group
                duplicate_info = {
                    'address': dedup_key[0][:50] + "..." if len(dedup_key[0]) > 50 else dedup_key[0],
                    'rooms': dedup_key[1],
                    'bedrooms': dedup_key[2],
                    'area': dedup_key[3],
                    'floor': dedup_key[4],
                    'total_floors': dedup_key[5],
                    'urban': dedup_key[6],
                    'duplicate_count': len(group_properties),
                    'kept_property': {
                        'id': best_property.id,
                        'price': best_property.price_total,
                        'user_type': best_property.user_type,
                        'user_title': best_property.user_title
                    },
                    'removed_properties': [
                        {
                            'id': prop.id,
                            'price': prop.price_total,
                            'user_type': prop.user_type,
                            'user_title': prop.user_title
                        }
                        for prop in sorted_properties[1:]
                    ]
                }
                duplicate_details.append(duplicate_info)
                
                logger.info(f"Duplicate group found:")
                logger.info(f"  Address: {duplicate_info['address']}")
                logger.info(f"  Details: {duplicate_info['rooms']} rooms, {duplicate_info['bedrooms']} bedrooms, {duplicate_info['area']} m²")
                logger.info(f"  Location: {duplicate_info['urban']}")
                logger.info(f"  Kept: ID {best_property.id} (Price: {best_property.price_total:,}, Type: {best_property.user_type})")
                for removed in duplicate_info['removed_properties']:
                    logger.info(f"  Removed: ID {removed['id']} (Price: {removed['price']:,}, Type: {removed['user_type']})")
        
        logger.info(f"Deduplication complete. Removed {duplicates_removed} duplicates from {len(property_groups)} groups.")
        logger.info(f"Final count: {len(deduplicated)} unique properties")
        
        # Save duplicate details
        if duplicate_details:
            with open('duplicate_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(duplicate_details, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved duplicate analysis to 'duplicate_analysis.json'")
        
        return deduplicated
    
    def save_properties(self, properties: List[Property], filename: str, include_raw: bool = False):
        """Save properties to JSON file with metadata"""
        data = {
            'metadata': {
                'total_properties': len(properties),
                'timestamp': datetime.now().isoformat(),
                'scraper_version': '2.0',
                'deduplication_applied': True
            },
            'properties': [
                prop.raw_data if include_raw else prop.to_dict() 
                for prop in properties
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(properties)} properties to {filename}")
    
    def get_statistics(self, properties: List[Property]) -> Dict:
        """Get comprehensive statistics about the scraped properties"""
        if not properties:
            return {}
        
        # Filter properties with valid prices for price statistics
        properties_with_price = [p for p in properties if p.price_total > 0]
        
        stats = {
            'total_properties': len(properties),
            'properties_with_price': len(properties_with_price),
            'by_deal_type': defaultdict(int),
            'by_real_estate_type': defaultdict(int),
            'by_user_type': defaultdict(int),
            'by_city': defaultdict(int),
            'by_district': defaultdict(int),
            'price_stats': {},
            'area_stats': {},
            'room_distribution': defaultdict(int),
            'floor_distribution': defaultdict(int)
        }
        
        if properties_with_price:
            prices = [p.price_total for p in properties_with_price]
            stats['price_stats'] = {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'median_price': sorted(prices)[len(prices) // 2]
            }
        
        areas = [p.area for p in properties if p.area > 0]
        if areas:
            stats['area_stats'] = {
                'min_area': min(areas),
                'max_area': max(areas),
                'avg_area': sum(areas) / len(areas),
                'median_area': sorted(areas)[len(areas) // 2]
            }
        
        for prop in properties:
            stats['by_deal_type'][prop.deal_type_id] += 1
            stats['by_real_estate_type'][prop.real_estate_type_id] += 1
            stats['by_user_type'][prop.user_type] += 1
            stats['by_city'][prop.city_name] += 1
            stats['by_district'][prop.district_name] += 1
            stats['room_distribution'][prop.room] += 1
            stats['floor_distribution'][str(prop.floor)] += 1
        
        return stats

def print_statistics(stats: Dict, title: str):
    """Print formatted statistics"""
    print(f"\n{title}")
    print("=" * len(title))
    
    print(f"Total properties: {stats.get('total_properties', 0)}")
    
    if 'price_stats' in stats and stats['price_stats']:
        print(f"\nPrice Statistics:")
        price_stats = stats['price_stats']
        print(f"  Min price: {price_stats['min_price']:,}")
        print(f"  Max price: {price_stats['max_price']:,}")
        print(f"  Avg price: {price_stats['avg_price']:,.2f}")
        print(f"  Median price: {price_stats['median_price']:,}")
    
    if 'area_stats' in stats and stats['area_stats']:
        print(f"\nArea Statistics:")
        area_stats = stats['area_stats']
        print(f"  Min area: {area_stats['min_area']} m²")
        print(f"  Max area: {area_stats['max_area']} m²")
        print(f"  Avg area: {area_stats['avg_area']:.2f} m²")
        print(f"  Median area: {area_stats['median_area']} m²")
    
    if 'by_user_type' in stats:
        print(f"\nBy User Type:")
        for user_type, count in stats['by_user_type'].items():
            print(f"  {user_type}: {count}")
    
    if 'by_city' in stats:
        print(f"\nTop 5 Cities:")
        sorted_cities = sorted(stats['by_city'].items(), key=lambda x: x[1], reverse=True)
        for city, count in sorted_cities[:5]:
            print(f"  {city}: {count}")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Real Estate Property Scraper')
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to scrape (default: all)')
    parser.add_argument('--cities', default='1', help='Cities parameter for API (default: 1)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--per-page', type=int, default=100, help='Items per page (default: 100, max: 100)')
    parser.add_argument('--output-dir', default='.', help='Output directory for files (default: current directory)')
    parser.add_argument('--include-raw', action='store_true', help='Include raw API data in output files')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode (max 3 pages)')
    
    args = parser.parse_args()
    
    # Set up output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Initialize scraper
    scraper = EnhancedPropertyScraper(delay=args.delay, per_page=getattr(args, 'per_page', 100))
    
    # Determine max pages
    max_pages = args.max_pages
    if args.test_mode:
        max_pages = 3
        print("Running in test mode - limiting to 3 pages")
    
    try:
        # Fetch all properties
        all_properties = scraper.fetch_all_properties(
            max_pages=max_pages, 
            cities=args.cities
        )
        
        if not all_properties:
            logger.error("No properties were fetched. Exiting.")
            return 1
        
        # Save raw properties
        raw_filename = os.path.join(args.output_dir, 'properties_raw.json')
        scraper.save_properties(all_properties, raw_filename, include_raw=args.include_raw)
        
        # Deduplicate properties
        unique_properties = scraper.deduplicate_properties(all_properties)
        
        # Save deduplicated properties
        unique_filename = os.path.join(args.output_dir, 'properties_unique.json')
        scraper.save_properties(unique_properties, unique_filename, include_raw=args.include_raw)
        
        # Generate and display statistics
        raw_stats = scraper.get_statistics(all_properties)
        unique_stats = scraper.get_statistics(unique_properties)
        
        print_statistics(raw_stats, "RAW PROPERTIES STATISTICS")
        print_statistics(unique_stats, "DEDUPLICATED PROPERTIES STATISTICS")
        
        print(f"\nSUMMARY")
        print("=" * 50)
        print(f"Raw properties fetched: {raw_stats['total_properties']}")
        print(f"Unique properties after deduplication: {unique_stats['total_properties']}")
        print(f"Duplicates removed: {raw_stats['total_properties'] - unique_stats['total_properties']}")
        
        print(f"\nFILES CREATED:")
        print(f"  - {raw_filename}")
        print(f"  - {unique_filename}")
        if os.path.exists('duplicate_analysis.json'):
            print(f"  - duplicate_analysis.json")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
