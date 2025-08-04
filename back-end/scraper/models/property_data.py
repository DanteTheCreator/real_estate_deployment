"""
Property data models for structured data handling.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PropertyImage:
    """Represents a property image."""
    
    url: str
    caption: Optional[str] = None
    is_primary: bool = False
    order_index: int = 0
    blur_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    local_path: Optional[str] = None  # For downloaded images
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'image_url': self.url,  # Database expects 'image_url' field
            'caption': self.caption,
            'is_primary': self.is_primary,
            'order_index': self.order_index
        }


@dataclass 
class PropertyParameter:
    """Represents a property parameter/amenity."""
    
    parameter_id: int
    parameter_value: Optional[str] = None
    parameter_select_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'parameter_id': self.parameter_id,
            'parameter_value': self.parameter_value,
            'parameter_select_name': self.parameter_select_name
        }


@dataclass
class PropertyPrice:
    """Represents a property price in a specific currency."""
    
    currency_type: str  # Currency ID from API
    price_total: float
    price_square: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'currency_type': self.currency_type,
            'price_total': self.price_total,
            'price_square': self.price_square
        }


@dataclass
class PropertyData:
    """Comprehensive property data structure."""
    
    # Basic identification
    external_id: str
    source: str = 'myhome.ge'
    
    # Multilingual content
    title: str = ''
    title_en: Optional[str] = None
    title_ru: Optional[str] = None
    description: str = ''
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    
    # Location
    address: str = ''
    city: str = 'Tbilisi'
    state: str = 'Georgia'
    country: str = 'Georgia'
    zip_code: Optional[str] = None
    district: Optional[str] = None
    urban_area: Optional[str] = None
    
    # Coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Property details
    property_type: str = 'apartment'
    listing_type: str = 'rent'
    bedrooms: int = 1
    bathrooms: float = 1.0
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    
    # Financial
    rent_amount: float = 0.0  # Primary amount in GEL
    rent_amount_usd: float = 0.0  # Amount in USD
    security_deposit: Optional[float] = None
    
    # Terms
    lease_duration: int = 12
    available_date: Optional[datetime] = None
    
    # Features
    is_available: bool = True
    is_furnished: bool = False
    pets_allowed: bool = False
    smoking_allowed: bool = False
    
    # Building details
    year_built: Optional[int] = None
    parking_spaces: int = 0
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    
    # Additional info
    utilities_included: str = ''
    user_type: str = 'agency'  # 'owner' or 'agency'
    
    # Metadata
    last_scraped: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Related data
    images: List[PropertyImage] = None
    parameters: List[PropertyParameter] = None
    prices: List[PropertyPrice] = None
    raw_parameters: List[Dict] = None  # Store raw parameter data for database parameter creation
    
    def __post_init__(self):
        """Initialize related data lists."""
        if self.images is None:
            self.images = []
        if self.parameters is None:
            self.parameters = []
        if self.prices is None:
            self.prices = []
        if self.raw_parameters is None:
            self.raw_parameters = []
    
    def add_image(self, url: str, **kwargs) -> PropertyImage:
        """Add an image to the property."""
        image = PropertyImage(url=url, **kwargs)
        self.images.append(image)
        return image
    
    def add_parameter(self, parameter_id: int, **kwargs) -> PropertyParameter:
        """Add a parameter to the property."""
        parameter = PropertyParameter(parameter_id=parameter_id, **kwargs)
        self.parameters.append(parameter)
        return parameter
    
    def add_price(self, currency_type: str, price_total: float, **kwargs) -> PropertyPrice:
        """Add a price to the property."""
        price = PropertyPrice(currency_type=currency_type, price_total=price_total, **kwargs)
        self.prices.append(price)
        return price
    
    def get_primary_image(self) -> Optional[PropertyImage]:
        """Get the primary image."""
        for image in self.images:
            if image.is_primary:
                return image
        return self.images[0] if self.images else None
    
    def get_price_by_currency(self, currency: str) -> Optional[PropertyPrice]:
        """Get price in specific currency."""
        for price in self.prices:
            if price.currency_type == currency:
                return price
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            'external_id': self.external_id,
            'source': self.source,
            'title': self.title,
            'title_en': self.title_en,
            'title_ru': self.title_ru,
            'description': self.description,
            'description_en': self.description_en,
            'description_ru': self.description_ru,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'zip_code': self.zip_code,
            'district': self.district,
            'urban_area': self.urban_area,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'property_type': self.property_type,
            'listing_type': self.listing_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'square_feet': self.square_feet,
            'lot_size': self.lot_size,
            'rent_amount': self.rent_amount,
            'rent_amount_usd': self.rent_amount_usd,
            'security_deposit': self.security_deposit,
            'lease_duration': self.lease_duration,
            'available_date': self.available_date,
            'is_available': self.is_available,
            'is_furnished': self.is_furnished,
            'pets_allowed': self.pets_allowed,
            'smoking_allowed': self.smoking_allowed,
            'year_built': self.year_built,
            'parking_spaces': self.parking_spaces,
            'floor_number': self.floor_number,
            'total_floors': self.total_floors,
            'utilities_included': self.utilities_included,
            'user_type': self.user_type,
            'last_scraped': self.last_scraped or datetime.now()
        }
