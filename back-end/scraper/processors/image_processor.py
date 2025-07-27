"""
Image processing for property images.
"""

import hashlib
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Import with fallbacks for Docker compatibility
try:
    from core.config import ScrapingConfig
    from models.property_data import PropertyData, PropertyImage
except ImportError:
    try:
        from ..core.config import ScrapingConfig
        from ..models.property_data import PropertyData, PropertyImage
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.models.property_data import PropertyData, PropertyImage


class ImageProcessor:
    """Handles property image processing and storage."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the image processor."""
        self.config = config
        self.storage_path = Path(config.image_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.image_hashes = {}  # For duplicate detection
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_property_images(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process and add images to property data."""
        try:
            images_data = raw_data.get('images', [])
            if not images_data:
                self.logger.debug(f"No images found for property {property_data.external_id}")
                return
            
            processed_count = 0
            for idx, image_data in enumerate(images_data):
                if not isinstance(image_data, dict):
                    continue
                
                # Extract image URLs
                image_url = (
                    image_data.get('large') or 
                    image_data.get('thumb') or 
                    image_data.get('small')
                )
                
                if not image_url:
                    continue
                
                # Skip duplicate images if enabled
                if self.config.enable_deduplication and self._is_duplicate_image(image_url):
                    self.logger.debug(f"Skipping duplicate image: {image_url}")
                    continue
                
                # Create PropertyImage object
                property_image = PropertyImage(
                    url=image_url,
                    caption=image_data.get('caption'),
                    is_primary=image_data.get('is_main', False) or idx == 0,
                    order_index=idx,
                    blur_url=image_data.get('blur'),
                    thumbnail_url=image_data.get('thumb')
                )
                
                # Download image if enabled
                if self.config.enable_image_download:
                    local_path = self._download_and_optimize_image(image_url, property_data.external_id)
                    if local_path:
                        property_image.local_path = local_path
                
                property_data.images.append(property_image)
                processed_count += 1
            
            self.logger.debug(f"Processed {processed_count} images for property {property_data.external_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing images for property {property_data.external_id}: {e}")
    
    def _is_duplicate_image(self, image_url: str) -> bool:
        """Check if image is a duplicate based on content hash."""
        try:
            image_hash = self._calculate_image_hash(image_url)
            if not image_hash:
                return False
            
            if image_hash in self.image_hashes:
                return True
            
            self.image_hashes[image_hash] = image_url
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking duplicate for image {image_url}: {e}")
            return False
    
    def _calculate_image_hash(self, image_url: str) -> str:
        """Calculate MD5 hash for image content."""
        try:
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Read first 8KB for hash calculation (enough for duplicate detection)
            content_chunk = response.raw.read(8192)
            return hashlib.md5(content_chunk).hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate hash for image {image_url}: {e}")
            return ""
    
    def _download_and_optimize_image(self, image_url: str, property_id: str) -> Optional[str]:
        """Download and store property image locally."""
        try:
            # Create property-specific directory
            property_dir = self.storage_path / f"property_{property_id}"
            property_dir.mkdir(exist_ok=True)
            
            # Generate filename from URL hash
            url_hash = hashlib.md5(image_url.encode()).hexdigest()
            extension = Path(urlparse(image_url).path).suffix or '.jpg'
            filename = f"{url_hash}{extension}"
            file_path = property_dir / filename
            
            # Skip if already downloaded
            if file_path.exists():
                self.logger.debug(f"Image already exists: {file_path}")
                return str(file_path)
            
            # Download image
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save image
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.debug(f"Downloaded image: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to download image {image_url}: {e}")
            return None
    
    def get_image_count(self, property_data: PropertyData) -> int:
        """Get total number of images for a property."""
        return len(property_data.images)
    
    def get_primary_image(self, property_data: PropertyData) -> Optional[PropertyImage]:
        """Get the primary image for a property."""
        return property_data.get_primary_image()
    
    def cleanup_orphaned_images(self, active_property_ids: List[str]) -> int:
        """Remove images for properties that no longer exist."""
        try:
            if not self.storage_path.exists():
                return 0
            
            cleaned_count = 0
            
            # Get all property directories
            for property_dir in self.storage_path.iterdir():
                if not property_dir.is_dir() or not property_dir.name.startswith('property_'):
                    continue
                
                # Extract property ID from directory name
                property_id = property_dir.name.replace('property_', '')
                
                # Remove if property is no longer active
                if property_id not in active_property_ids:
                    try:
                        # Remove all files in directory
                        for file_path in property_dir.iterdir():
                            if file_path.is_file():
                                file_path.unlink()
                        
                        # Remove directory
                        property_dir.rmdir()
                        cleaned_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to cleanup directory {property_dir}: {e}")
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} orphaned image directories")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error during image cleanup: {e}")
            return 0
