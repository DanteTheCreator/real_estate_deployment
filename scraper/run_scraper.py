#!/usr/bin/env python3
"""
Real Estate Scraper - Cron Entry Point
Simple, reliable script for scheduled property scraping with full data capture
"""

import sys
import os
import logging
import time
from datetime import datetime
from pathlib import Path

# Add the scraper directory to Python path
scraper_dir = Path(__file__).parent
sys.path.insert(0, str(scraper_dir))

# Set up logging for cron jobs
log_dir = scraper_dir / "logs"
log_dir.mkdir(exist_ok=True)

log_filename = log_dir / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)  # Also log to stdout for cron
    ]
)
logger = logging.getLogger(__name__)

def run_scraper():
    """Run the property scraper with full data capture"""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Starting Real Estate Scraper - Full Data Capture")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    try:
        from scrape_to_db import run_scraper_to_database
        
        # Run the complete scraper pipeline
        result = run_scraper_to_database(
            max_pages=None,  # Scrape all pages
            cities='1',      # Tbilisi
            delay=1.0,       # Conservative delay
            batch_size=50,   # Smaller batches for stability
            skip_existing=True,  # Skip existing properties
            test_mode=False,     # Full production run
            save_files=True,     # Save JSON files for backup
            cleanup_first=False  # Don't cleanup existing data
        )
        
        if result.get('success', False):
            logger.info("Scraper completed successfully!")
            logger.info(f"Results: {result}")
        else:
            logger.error(f"Scraper failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Critical error in scraper: {e}", exc_info=True)
        return 1
    
    finally:
        elapsed = time.time() - start_time
        logger.info(f"Scraper execution time: {elapsed:.2f} seconds")
        logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = run_scraper()
    sys.exit(exit_code)
