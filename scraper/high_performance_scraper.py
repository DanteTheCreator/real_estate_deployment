#!/usr/bin/env python3
"""
High-Performance Property Scraper with Concurrent Processing
Optimized for maximum throughput and efficient resource usage
"""

import asyncio
import aiohttp
import time
import json
import logging
import argparse
import sys
import os
from typing import List, Dict, Set, Tuple, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime
import concurrent.futures
from threading import Lock
import sqlite3
from pathlib import Path
import psutil
import signal

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
        normalized_address = self.address.lower().strip().replace('  ', ' ')
        return (
            normalized_address,
            self.room,
            self.bedroom,
            self.area,
            round(self.lat, 4) if self.lat else 0,
            round(self.lng, 4) if self.lng else 0,
            self.city_name.lower().strip() if self.city_name else '',
            self.deal_type_id,
            self.real_estate_type_id
        )
    
    @property
    def is_owner(self) -> bool:
        """Check if this is a property posted by owner (not agent)"""
        return self.user_type == 'physical'
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding raw_data"""
        return {k: v for k, v in asdict(self).items() if k != 'raw_data'}

class HighPerformancePropertyScraper:
    """
    High-performance scraper with concurrent processing, smart rate limiting,
    and optimized memory usage
    """
    
    def __init__(self, 
                 max_concurrent_requests: int = 50,
                 request_delay: float = 0.1,
                 timeout: int = 30,
                 max_retries: int = 5,
                 use_cache: bool = True,
                 memory_limit_mb: int = 2048,
                 per_page: int = 100):
        
        self.base_url = 'https://api-statements.tnet.ge/v1/statements'
        self.per_page = per_page
        self.max_concurrent = max_concurrent_requests
        self.request_delay = request_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_cache = use_cache
        self.memory_limit = memory_limit_mb * 1024 * 1024  # Convert to bytes
        
        # Thread-safe counters and storage
        self.processed_count = 0
        self.error_count = 0
        self.duplicate_count = 0
        self.cache_hits = 0
        self.lock = Lock()
        
        # In-memory cache for deduplication
        self.seen_properties: Set[Tuple] = set()
        self.property_buffer: List[Property] = []
        
        # Rate limiting
        self.last_request_time = 0
        self.request_semaphore = None
        
        # Cache database for persistence across runs
        self.cache_db_path = "scraper_cache.db" if use_cache else None
        self.setup_cache_db()
        
        # Graceful shutdown handling
        self.shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def setup_cache_db(self):
        """Setup SQLite cache database for persistence"""
        if not self.cache_db_path:
            return
            
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS property_cache (
                        id INTEGER PRIMARY KEY,
                        dedup_key TEXT UNIQUE,
                        data TEXT,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dedup_key ON property_cache(dedup_key)
                ''')
                conn.commit()
                logger.info("Cache database initialized")
        except Exception as e:
            logger.warning(f"Failed to setup cache database: {e}")
            self.cache_db_path = None
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is within limits"""
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss
        return memory_usage < self.memory_limit
    
    async def create_session(self) -> aiohttp.ClientSession:
        """Create optimized aiohttp session"""
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent * 2,
            limit_per_host=self.max_concurrent,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,ka;q=0.8,und;q=0.7',
            'global-authorization': '',
            'locale': 'ka',
            'origin': 'https://www.myhome.ge',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-website-key': 'myhome',
        }
        
        return aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )
    
    async def fetch_page_async(self, session: aiohttp.ClientSession, page: int, 
                              cities: str = '1') -> Optional[Dict]:
        """Fetch a single page asynchronously with advanced error handling"""
        params = {
            'page': str(page),
            'per_page': str(self.per_page),
        }
        
        # Rate limiting
        if self.request_semaphore:
            await self.request_semaphore.acquire()
        
        # Respect request delay
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = time.time()
        
        for attempt in range(self.max_retries):
            if self.shutdown_requested:
                return None
                
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if self.request_semaphore:
                            self.request_semaphore.release()
                        return data
                    elif response.status == 429:  # Rate limited
                        wait_time = min(2 ** attempt, 60)  # Max 60 seconds
                        logger.warning(f"Rate limited on page {page}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for page {page}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on page {page}, attempt {attempt + 1}")
            except Exception as e:
                logger.warning(f"Error fetching page {page}, attempt {attempt + 1}: {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(min(2 ** attempt, 10))
        
        if self.request_semaphore:
            self.request_semaphore.release()
            
        with self.lock:
            self.error_count += 1
        
        logger.error(f"Failed to fetch page {page} after {self.max_retries} attempts")
        return None
    
    def parse_property(self, property_data: Dict) -> Optional[Property]:
        """Parse raw property data into Property object with enhanced validation"""
        try:
            # Get price in the primary currency
            price_data = property_data.get('price', {})
            price_total = 0
            if '1' in price_data:
                price_total = price_data['1'].get('price_total', 0)
            elif price_data:
                first_currency = list(price_data.keys())[0]
                price_total = price_data[first_currency].get('price_total', 0)
            
            # Get user type
            user_type_data = property_data.get('user_type', {})
            user_type = user_type_data.get('type', 'unknown')
            
            # Basic validation
            property_id = property_data.get('id')
            if not property_id:
                return None
            
            # Create property object
            prop = Property(
                id=property_id,
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
                lat=float(property_data.get('lat', 0) or 0),
                lng=float(property_data.get('lng', 0) or 0),
                last_updated=property_data.get('last_updated', ''),
                user_title=property_data.get('user_title', ''),
                comment=property_data.get('comment', ''),
                raw_data=property_data
            )
            
            # Inline deduplication check
            dedup_key = prop.dedup_key
            if dedup_key in self.seen_properties:
                with self.lock:
                    self.duplicate_count += 1
                return None
            
            self.seen_properties.add(dedup_key)
            return prop
            
        except Exception as e:
            logger.error(f"Error parsing property {property_data.get('id', 'unknown')}: {e}")
            return None
    
    async def process_page_batch(self, session: aiohttp.ClientSession, 
                                page_numbers: List[int], cities: str = '1') -> List[Property]:
        """Process a batch of pages concurrently"""
        tasks = [
            self.fetch_page_async(session, page, cities) 
            for page in page_numbers
        ]
        
        page_results = await asyncio.gather(*tasks, return_exceptions=True)
        properties = []
        
        for page_num, result in zip(page_numbers, page_results):
            if isinstance(result, Exception):
                logger.error(f"Exception processing page {page_num}: {result}")
                continue
                
            if not result or not isinstance(result, dict) or not result.get('result'):
                continue
            
            properties_data = result.get('data', {}).get('data', [])
            if not properties_data:
                continue
            
            # Process properties in this page
            page_properties = []
            for prop_data in properties_data:
                prop = self.parse_property(prop_data)
                if prop:
                    page_properties.append(prop)
            
            properties.extend(page_properties)
            
            with self.lock:
                self.processed_count += len(properties_data)
            
            logger.info(f"Page {page_num}: {len(page_properties)} unique properties "
                       f"({len(properties_data)} total, {self.per_page} per page)")
        
        return properties
    
    async def scrape_all_properties_async(self, 
                                        max_pages: Optional[int] = None,
                                        cities: str = '1',
                                        batch_size: int = 20,
                                        max_empty_batches: int = 5) -> AsyncGenerator[List[Property], None]:
        """
        Scrape all properties using concurrent processing with intelligent batching
        """
        logger.info(f"Starting high-performance scraping with {self.max_concurrent} concurrent requests")
        
        # Initialize semaphore for rate limiting
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent)
        
        all_properties = []
        page = 1
        empty_batches = 0
        
        async with await self.create_session() as session:
            while True:
                if self.shutdown_requested:
                    logger.info("Shutdown requested, stopping scraping")
                    break
                
                if max_pages and page > max_pages:
                    logger.info(f"Reached max pages limit: {max_pages}")
                    break
                
                if empty_batches >= max_empty_batches:
                    logger.info(f"Reached {max_empty_batches} consecutive empty batches, stopping")
                    break
                
                # Check memory usage
                if not self.check_memory_usage():
                    logger.warning("Memory limit reached, processing current batch and stopping")
                    break
                
                # Create batch of page numbers
                batch_pages = list(range(page, min(page + batch_size, (max_pages or 9999) + 1)))
                if not batch_pages:
                    break
                
                logger.info(f"Processing batch: pages {batch_pages[0]} to {batch_pages[-1]}")
                
                # Process batch concurrently
                batch_properties = await self.process_page_batch(session, batch_pages, cities)
                
                if not batch_properties:
                    empty_batches += 1
                    logger.info(f"Empty batch {empty_batches}/{max_empty_batches}")
                else:
                    empty_batches = 0
                    all_properties.extend(batch_properties)
                    
                    # Periodically flush to prevent memory buildup
                    if len(all_properties) > 10000:
                        logger.info(f"Flushing {len(all_properties)} properties to prevent memory buildup")
                        yield all_properties
                        all_properties = []
                
                page = batch_pages[-1] + 1
                
                # Progress reporting
                if page % 100 == 0:
                    logger.info(f"Progress: Page {page}, Processed: {self.processed_count}, "
                              f"Unique: {len(all_properties)}, Duplicates: {self.duplicate_count}, "
                              f"Errors: {self.error_count}")
        
        if all_properties:
            yield all_properties
        
        logger.info(f"Scraping complete. Final stats - Processed: {self.processed_count}, "
                   f"Duplicates: {self.duplicate_count}, Errors: {self.error_count}")
    
    async def save_properties_streaming_async(self, properties_generator: AsyncGenerator[List[Property], None], 
                                         base_filename: str) -> str:
        """Save properties in streaming fashion to handle large datasets"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.json"
        
        total_saved = 0
        batch_num = 0
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('{\n  "metadata": {\n')
            f.write(f'    "timestamp": "{datetime.now().isoformat()}",\n')
            f.write('    "scraper_version": "3.0-high-performance",\n')
            f.write('    "streaming": true\n')
            f.write('  },\n  "properties": [\n')
            
            first_batch = True
            
            async for property_batch in properties_generator:
                if not first_batch:
                    f.write(',\n')
                first_batch = False
                
                batch_data = [prop.to_dict() for prop in property_batch]
                batch_json = json.dumps(batch_data, ensure_ascii=False, indent=4)
                # Remove outer brackets and add proper indentation
                batch_content = batch_json[1:-1].replace('\n', '\n    ')
                f.write(f'    {batch_content}')
                
                total_saved += len(property_batch)
                batch_num += 1
                
                logger.info(f"Saved batch {batch_num} with {len(property_batch)} properties. "
                           f"Total: {total_saved}")
            
            f.write('\n  ]\n}')
        
        logger.info(f"Streaming save complete: {total_saved} properties saved to {filename}")
        return filename

async def main():
    """Main function with advanced argument parsing and execution"""
    parser = argparse.ArgumentParser(
        description="High-Performance Property Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # High-speed scraping with 100 concurrent requests
  python high_performance_scraper.py --concurrent 100 --delay 0.05

  # Memory-conscious scraping for large datasets
  python high_performance_scraper.py --memory-limit 4096 --batch-size 50

  # Quick test run
  python high_performance_scraper.py --max-pages 10 --test-mode
        """
    )
    
    parser.add_argument('--max-pages', type=int, 
                       help='Maximum number of pages to scrape')
    parser.add_argument('--cities', default='1', 
                       help='Cities parameter for API (default: 1)')
    parser.add_argument('--concurrent', type=int, default=50,
                       help='Maximum concurrent requests (default: 50)')
    parser.add_argument('--delay', type=float, default=0.1,
                       help='Delay between requests in seconds (default: 0.1)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    parser.add_argument('--batch-size', type=int, default=20,
                       help='Pages to process in each batch (default: 20)')
    parser.add_argument('--memory-limit', type=int, default=2048,
                       help='Memory limit in MB (default: 2048)')
    parser.add_argument('--per-page', type=int, default=100,
                       help='Number of items per page (default: 100, max: 100)')
    parser.add_argument('--output', default='properties_hp',
                       help='Output filename base (default: properties_hp)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable caching')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode (limited pages)')
    
    args = parser.parse_args()
    
    if args.test_mode:
        args.max_pages = min(args.max_pages or 10, 10)
        args.concurrent = min(args.concurrent, 10)
        logger.info("Running in test mode with limited pages and concurrency")
    
    try:
        # Initialize scraper
        scraper = HighPerformancePropertyScraper(
            max_concurrent_requests=args.concurrent,
            request_delay=args.delay,
            timeout=args.timeout,
            use_cache=not args.no_cache,
            memory_limit_mb=args.memory_limit,
            per_page=min(args.per_page, 100)  # API max is 100
        )
        
        logger.info(f"Starting scraper with configuration:")
        logger.info(f"  - Max concurrent requests: {args.concurrent}")
        logger.info(f"  - Request delay: {args.delay}s")
        logger.info(f"  - Batch size: {args.batch_size}")
        logger.info(f"  - Per page: {scraper.per_page} items")
        logger.info(f"  - Memory limit: {args.memory_limit}MB")
        logger.info(f"  - Max pages: {args.max_pages or 'unlimited'}")
        
        start_time = time.time()
        
        # Run scraping
        properties_generator = scraper.scrape_all_properties_async(
            max_pages=args.max_pages,
            cities=args.cities,
            batch_size=args.batch_size
        )
        
        # Save results in streaming fashion
        output_file = await scraper.save_properties_streaming_async(properties_generator, args.output)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Scraping completed in {duration:.2f} seconds")
        logger.info(f"Final statistics:")
        logger.info(f"  - Total processed: {scraper.processed_count}")
        logger.info(f"  - Duplicates removed: {scraper.duplicate_count}")
        logger.info(f"  - Errors: {scraper.error_count}")
        logger.info(f"  - Average speed: {scraper.processed_count/duration:.2f} properties/second")
        logger.info(f"  - Output file: {output_file}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    # Set up event loop policy for Windows compatibility
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    sys.exit(asyncio.run(main()))
