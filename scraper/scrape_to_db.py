#!/usr/bin/env python3
"""
Comprehensive scraper script that fetches properties and saves them to the database
Combines scraping and database integration
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import local modules
from enhanced_scraper import EnhancedPropertyScraper, print_statistics
from database_integration import DatabaseIntegrator, test_database_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scraper_to_database(
    max_pages: Optional[int] = None,
    cities: str = '1',
    delay: float = 1.0,
    batch_size: int = 100,
    skip_existing: bool = True,
    test_mode: bool = False,
    save_files: bool = True,
    cleanup_first: bool = False
) -> dict:
    """
    Run the complete scraper pipeline: fetch properties and save to database
    
    Args:
        max_pages: Maximum number of pages to scrape
        cities: Cities parameter for API
        delay: Delay between requests
        batch_size: Batch size for database operations
        skip_existing: Whether to skip existing properties
        test_mode: Run in test mode (limited pages)
        save_files: Whether to save JSON files
        cleanup_first: Whether to cleanup existing scraped properties first
        
    Returns:
        Dictionary with operation statistics
    """
    
    logger.info("Starting scraper to database pipeline...")
    
    # Test database connection first
    if not test_database_connection():
        logger.error("Database connection failed. Cannot proceed.")
        return {"success": False, "error": "Database connection failed"}
    
    # Initialize components
    scraper = EnhancedPropertyScraper(delay=delay)
    db_integrator = DatabaseIntegrator()
    
    # Cleanup existing properties if requested
    if cleanup_first:
        logger.info("Cleaning up existing scraped properties...")
        deleted_count = db_integrator.cleanup_system_properties()
        logger.info(f"Deleted {deleted_count} existing properties")
    
    # Get initial database stats
    initial_count = db_integrator.get_property_count()
    logger.info(f"Database has {initial_count} properties before scraping")
    
    try:
        # Determine max pages for test mode
        if test_mode:
            max_pages = 3
            logger.info("Running in test mode - limiting to 3 pages")
        
        # Fetch properties
        logger.info(f"Starting to scrape properties (max_pages: {max_pages}, cities: {cities})")
        all_properties = scraper.fetch_all_properties(max_pages=max_pages, cities=cities)
        
        if not all_properties:
            logger.error("No properties were fetched. Exiting.")
            return {"success": False, "error": "No properties fetched"}
        
        logger.info(f"Fetched {len(all_properties)} raw properties")
        
        # Deduplicate properties using scraper logic
        logger.info("Deduplicating properties...")
        unique_properties = scraper.deduplicate_properties(all_properties)
        logger.info(f"After deduplication: {len(unique_properties)} unique properties")
        
        # Save to database
        logger.info("Saving properties to database...")
        db_stats = db_integrator.save_properties_to_db(
            unique_properties,
            batch_size=batch_size,
            skip_existing=skip_existing
        )
        
        # Get final database stats
        final_count = db_integrator.get_property_count()
        
        # Save to files if requested
        file_stats = {}
        if save_files:
            logger.info("Saving properties to JSON files...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            raw_filename = f'properties_raw_{timestamp}.json'
            unique_filename = f'properties_unique_{timestamp}.json'
            
            scraper.save_properties(all_properties, raw_filename)
            scraper.save_properties(unique_properties, unique_filename)
            
            file_stats = {
                "raw_file": raw_filename,
                "unique_file": unique_filename
            }
        
        # Generate statistics
        raw_stats = scraper.get_statistics(all_properties)
        unique_stats = scraper.get_statistics(unique_properties)
        
        # Print comprehensive results
        print("\n" + "="*80)
        print("SCRAPER TO DATABASE PIPELINE RESULTS")
        print("="*80)
        
        print(f"\nSCRAPING STATISTICS:")
        print(f"  Raw properties fetched: {len(all_properties)}")
        print(f"  Unique properties after deduplication: {len(unique_properties)}")
        print(f"  Duplicates removed by scraper: {len(all_properties) - len(unique_properties)}")
        
        print(f"\nDATABASE STATISTICS:")
        print(f"  Properties before scraping: {initial_count}")
        print(f"  Properties after scraping: {final_count}")
        print(f"  New properties added: {db_stats['saved']}")
        print(f"  Existing properties skipped: {db_stats['skipped']}")
        print(f"  Errors during save: {db_stats['errors']}")
        print(f"  Total processed: {db_stats['total_processed']}")
        
        if file_stats:
            print(f"\nFILES SAVED:")
            print(f"  Raw properties: {file_stats['raw_file']}")
            print(f"  Unique properties: {file_stats['unique_file']}")
        
        # Print detailed statistics
        print_statistics(raw_stats, "\nRAW PROPERTIES STATISTICS")
        print_statistics(unique_stats, "\nUNIQUE PROPERTIES STATISTICS")
        
        return {
            "success": True,
            "scraping": {
                "raw_count": len(all_properties),
                "unique_count": len(unique_properties),
                "duplicates_removed": len(all_properties) - len(unique_properties)
            },
            "database": {
                "initial_count": initial_count,
                "final_count": final_count,
                "saved": db_stats["saved"],
                "skipped": db_stats["skipped"],
                "errors": db_stats["errors"]
            },
            "files": file_stats
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Scrape properties and save to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test-mode                    # Run in test mode (3 pages)
  %(prog)s --max-pages 10                 # Scrape max 10 pages
  %(prog)s --cleanup-first                # Clean existing data first
  %(prog)s --no-skip-existing             # Don't skip existing properties
  %(prog)s --no-save-files                # Don't save JSON files
        """
    )
    
    parser.add_argument('--max-pages', type=int, 
                       help='Maximum number of pages to scrape (default: all)')
    parser.add_argument('--cities', default='1', 
                       help='Cities parameter for API (default: 1)')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for database operations (default: 100)')
    parser.add_argument('--no-skip-existing', action='store_true',
                       help='Don\'t skip existing properties (allow duplicates)')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode (max 3 pages)')
    parser.add_argument('--no-save-files', action='store_true',
                       help='Don\'t save JSON files')
    parser.add_argument('--cleanup-first', action='store_true',
                       help='Remove existing scraped properties before starting')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the pipeline
    result = run_scraper_to_database(
        max_pages=args.max_pages,
        cities=args.cities,
        delay=args.delay,
        batch_size=args.batch_size,
        skip_existing=not args.no_skip_existing,
        test_mode=args.test_mode,
        save_files=not args.no_save_files,
        cleanup_first=args.cleanup_first
    )
    
    if result["success"]:
        print("\n✅ Scraper to database pipeline completed successfully!")
        return 0
    else:
        print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
