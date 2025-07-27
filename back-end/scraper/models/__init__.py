"""
Data models for the scraper system.
"""

from .statistics import ScrapingStats
from .property_data import PropertyData, PropertyImage, PropertyParameter, PropertyPrice

__all__ = [
    'ScrapingStats',
    'PropertyData',
    'PropertyImage', 
    'PropertyParameter',
    'PropertyPrice'
]
