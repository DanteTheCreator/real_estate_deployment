"""
Advanced MyHome.ge Property Scraper - Refactored

A modular, production-ready scraper for MyHome.ge property data with
advanced features including multilingual support, deduplication,
and comprehensive error handling.

Author: Production Team
Version: 2.0.0 (Refactored)

Main Components:
- Core: Base classes, configuration, and exceptions
- Models: Data structures and statistics
- Processors: Data processing components
- Services: Business logic services  
- Utils: Utility functions and validation

Usage:
    from scraper import MyHomeAdvancedScraper, ScrapingConfig
    
    config = ScrapingConfig(max_properties=500)
    scraper = MyHomeAdvancedScraper(config)
    stats = await scraper.scrape()
"""

from .core import ScrapingConfig, BaseScraper
from .myhome_scraper import MyHomeAdvancedScraper
from .models import ScrapingStats, PropertyData

__version__ = "2.0.0"
__author__ = "Production Team"

__all__ = [
    # Core components
    'ScrapingConfig',
    'BaseScraper',
    
    # Main scraper
    'MyHomeAdvancedScraper',
    'scrape_properties',
    
    # Data models
    'ScrapingStats',
    'PropertyData',
    
    # Version info
    '__version__',
    '__author__'
]
