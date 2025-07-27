"""
Base scraper class providing common functionality.
"""

import logging
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from sqlalchemy.orm import Session

from .config import ScrapingConfig

# Try absolute imports for Docker compatibility
try:
    from models.statistics import ScrapingStats
except ImportError:
    try:
        from scraper.models.statistics import ScrapingStats
    except ImportError:
        from ..models.statistics import ScrapingStats


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the scraper with configuration."""
        self.config = config
        self.stats = ScrapingStats(start_time=datetime.now())
        self.session = requests.Session()
        self.request_times = []
        
        # Validate configuration
        config_errors = config.validate()
        if config_errors:
            raise ValueError(f"Configuration validation failed: {', '.join(config_errors)}")
        
        # Setup logging
        self._setup_logging()
        
        # Setup HTTP session
        self._setup_session()
        
        self.logger.info(f"Initialized {self.__class__.__name__} with config")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_dir = Path(self.config.log_directory)
        
        # Create logger for this scraper instance
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{id(self)}")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Console handler (always works)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # Try to add file handler if possible
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                log_filename = log_dir / f'{self.__class__.__name__.lower()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
                file_handler = logging.FileHandler(log_filename, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except (PermissionError, OSError) as e:
                # If file logging fails, just log to console
                self.logger.warning(f"Could not create log file: {e}. Logging to console only.")
    
    def _setup_session(self) -> None:
        """Setup HTTP session with proper headers."""
        if not self.config.user_agents:
            raise ConfigurationError("No user agents configured")
        
        user_agent = self.config.user_agents[0]
        
        self.session.headers.update({
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
            'user-agent': user_agent,
            'x-website-key': 'myhome'
        })
        
        self.logger.debug("HTTP session configured")
    
    def _rotate_user_agent(self) -> None:
        """Rotate user agent to avoid detection."""
        user_agent = random.choice(self.config.user_agents)
        self.session.headers['user-agent'] = user_agent
        self.logger.debug(f"Rotated user agent: {user_agent[:50]}...")
    
    def _respect_rate_limit(self) -> None:
        """Implement rate limiting to avoid being blocked."""
        now = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Check if we've hit the rate limit
        if len(self.request_times) >= self.config.rate_limit_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                self.logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def make_request(self, url: str, params: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, method: str = 'GET') -> requests.Response:
        """Make an HTTP request with rate limiting and retries."""
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        
        # Merge custom headers with session headers
        request_headers = {**self.session.headers, **headers}
        
        for attempt in range(self.config.max_retries):
            try:
                # Apply rate limiting
                self._respect_rate_limit()
                
                # Rotate user agent occasionally
                if random.random() < 0.1:  # 10% chance
                    self._rotate_user_agent()
                
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                # Make the request
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=request_headers,
                    timeout=self.config.timeout
                )
                
                # Check for success
                response.raise_for_status()
                
                self.stats.api_calls += 1
                self.logger.debug(f"Request successful: {response.status_code}")
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                
                if attempt < self.config.max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * self.config.delay_between_requests
                    self.logger.debug(f"Waiting {wait_time:.2f} seconds before retry")
                    time.sleep(wait_time)
                else:
                    self.stats.errors += 1
                    raise NetworkError(f"Max retries exceeded for {url}: {e}")
            
            except Exception as e:
                self.logger.error(f"Unexpected error making request to {url}: {e}")
                self.stats.errors += 1
                raise RuntimeError(f"Request failed: {e}")
        
        # Should never reach here, but just in case
        raise NetworkError(f"Failed to make request to {url}")
    
    def create_directories(self) -> None:
        """Create necessary directories for operation."""
        directories = [
            self.config.image_storage_path,
            self.config.log_directory,
            self.config.reports_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    @abstractmethod
    def scrape(self, **kwargs) -> ScrapingStats:
        """Main scraping method to be implemented by subclasses."""
        pass
    
    @abstractmethod
    def validate_property_data(self, property_data: Dict) -> bool:
        """Validate property data specific to the scraper source."""
        pass
    
    def finalize(self) -> None:
        """Cleanup operations to be called when scraping is complete."""
        self.stats.end_time = datetime.now()
        duration = (self.stats.end_time - self.stats.start_time).total_seconds()
        
        self.logger.info(f"Scraping completed in {duration:.2f} seconds")
        self.logger.info(f"Total API calls: {self.stats.api_calls}")
        self.logger.info(f"Total errors: {self.stats.errors}")
        
        # Close session
        self.session.close()
        
        # Close logging handlers
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
