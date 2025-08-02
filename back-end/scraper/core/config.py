"""
Configuration management for the scraper system.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class ScrapingConfig:
    """Configuration for the scraper."""
    
    # Basic scraping settings
    max_properties: int = 50000  # Increased to handle more properties
    batch_size: int = 50
    delay_between_requests: float = 0.01  # Much faster - 10ms between requests
    max_retries: int = 3
    timeout: int = 30
    cleanup_days: int = 30
    
    # Feature toggles
    concurrent_languages: bool = True  # Always enabled for multilingual
    enable_image_download: bool = False
    enable_deduplication: bool = True
    enable_owner_priority: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 600
    
    # Storage paths
    image_storage_path: str = "/app/data/property_images"
    log_directory: str = "/app/logs"
    reports_directory: str = "/app/data/reports"
    
    # User agents for rotation
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
    ])
    
    # API endpoints
    api_endpoints: Dict[str, str] = field(default_factory=lambda: {
        'list_properties': 'https://api-statements.tnet.ge/v1/statements',
        'property_details': 'https://api-statements.tnet.ge/v1/statements'
    })
    
    # Property type mappings
    property_types: Dict[int, str] = field(default_factory=lambda: {
        1: "apartment",
        2: "house",
        3: "commercial", 
        4: "country_house",
        5: "land_plot",
        6: "hotel"
    })
    
    # Default property types to scrape (all types)
    default_property_types: str = "2,1,3,4,5,6"  # house, apartment, commercial, country_house, land_plot, hotel
    
    # Deal type mappings
    deal_types: Dict[int, str] = field(default_factory=lambda: {
        1: "sale",           # იყიდება (for sale)
        2: "rent",           # ქირავდება (for rent)
        3: "lease",          # გაიცემა იჯარით (given for lease)
        4: "mortgage",       # გირავდება (mortgage/collateral)
        7: "daily_rent"      # ქირავდება დღიურად (daily rent)
    })
    
    # Default deal types to scrape (all types)
    default_deal_types: str = "1,2,3,4,7"  # sale, rent, lease, mortgage, daily_rent
    
    # API pagination settings
    per_page: int = 1000  # Maximum properties per API request (updated to 10k)
    
    # Default deal types to scrape (all types)
    default_deal_types: str = "1,2,3,7"  # sale, rent, lease, daily_rent
    
    # Currency mappings
    currency_types: Dict[int, str] = field(default_factory=lambda: {
        1: "USD",
        2: "GEL",
        3: "EUR"
    })
    
    # Supported languages
    languages: List[str] = field(default_factory=lambda: ['ka', 'en', 'ru'])
    
    # Validation settings
    coordinate_bounds: Dict[str, float] = field(default_factory=lambda: {
        'lat_min': 40.0,
        'lat_max': 43.6,
        'lng_min': 39.8,
        'lng_max': 46.7
    })
    
    # Price validation ranges by currency
    price_ranges: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        'USD': {'min': 50, 'max': 50000},
        'GEL': {'min': 135, 'max': 135000},
        'EUR': {'min': 45, 'max': 45000}
    })

    @classmethod
    def from_file(cls, config_path: str) -> 'ScrapingConfig':
        """Load configuration from a YAML file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise ValueError(f"Configuration file not found: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                raise ValueError("Configuration file is empty")
            
            # Create instance with defaults and update with file data
            instance = cls()
            
            # Update only existing attributes to avoid invalid configs
            for key, value in config_data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    # Log warning for unknown config keys but don't fail
                    import logging
                    logging.warning(f"Unknown configuration key: {key}")
            
            return instance
            
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """Create configuration from environment variables."""
        instance = cls()
        
        # Map environment variables to config attributes
        env_mappings = {
            'SCRAPER_MAX_PROPERTIES': ('max_properties', int),
            'SCRAPER_BATCH_SIZE': ('batch_size', int),
            'SCRAPER_DELAY': ('delay_between_requests', float),
            'SCRAPER_MAX_RETRIES': ('max_retries', int),
            'SCRAPER_TIMEOUT': ('timeout', int),
            'SCRAPER_CLEANUP_DAYS': ('cleanup_days', int),
            'SCRAPER_CONCURRENT_LANGUAGES': ('concurrent_languages', lambda x: x.lower() == 'true'),
            'SCRAPER_ENABLE_IMAGES': ('enable_image_download', lambda x: x.lower() == 'true'),
            'SCRAPER_ENABLE_DEDUP': ('enable_deduplication', lambda x: x.lower() == 'true'),
            'SCRAPER_OWNER_PRIORITY': ('enable_owner_priority', lambda x: x.lower() == 'true'),
            'SCRAPER_RATE_LIMIT': ('rate_limit_per_minute', int),
            'SCRAPER_IMAGE_PATH': ('image_storage_path', str),
            'SCRAPER_LOG_DIR': ('log_directory', str),
            'SCRAPER_REPORTS_DIR': ('reports_directory', str)
        }
        
        for env_var, (attr_name, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    setattr(instance, attr_name, converted_value)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value for {env_var}: {env_value} ({e})")
        
        return instance
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate numeric ranges
        if self.max_properties <= 0:
            errors.append("max_properties must be positive")
        
        if self.batch_size <= 0 or self.batch_size > 1000:
            errors.append("batch_size must be between 1 and 1000")
        
        if self.delay_between_requests < 0:
            errors.append("delay_between_requests cannot be negative")
        
        if self.max_retries < 1:
            errors.append("max_retries must be at least 1")
        
        if self.timeout <= 0:
            errors.append("timeout must be positive")
        
        if self.cleanup_days < 0:
            errors.append("cleanup_days cannot be negative")
        
        if self.rate_limit_per_minute <= 0:
            errors.append("rate_limit_per_minute must be positive")
        
        # Validate lists
        if not self.user_agents:
            errors.append("user_agents list cannot be empty")
        
        if not self.languages:
            errors.append("languages list cannot be empty")
        
        # Validate URLs
        for endpoint_name, url in self.api_endpoints.items():
            if not url or not url.startswith(('http://', 'https://')):
                errors.append(f"Invalid URL for {endpoint_name}: {url}")
        
        # Validate paths
        for path_name in ['image_storage_path', 'log_directory', 'reports_directory']:
            path = getattr(self, path_name)
            if not path:
                errors.append(f"{path_name} cannot be empty")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'max_properties': self.max_properties,
            'batch_size': self.batch_size,
            'delay_between_requests': self.delay_between_requests,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'cleanup_days': self.cleanup_days,
            'concurrent_languages': self.concurrent_languages,
            'enable_image_download': self.enable_image_download,
            'enable_deduplication': self.enable_deduplication,
            'enable_owner_priority': self.enable_owner_priority,
            'rate_limit_per_minute': self.rate_limit_per_minute,
            'image_storage_path': self.image_storage_path,
            'log_directory': self.log_directory,
            'reports_directory': self.reports_directory,
            'user_agents': self.user_agents.copy(),
            'api_endpoints': self.api_endpoints.copy(),
            'property_types': self.property_types.copy(),
            'deal_types': self.deal_types.copy(),
            'currency_types': self.currency_types.copy(),
            'languages': self.languages.copy(),
            'coordinate_bounds': self.coordinate_bounds.copy(),
            'price_ranges': self.price_ranges.copy()
        }
