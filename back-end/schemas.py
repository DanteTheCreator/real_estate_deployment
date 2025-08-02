from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    COUNTRY_HOUSE = "country_house"
    LAND_PLOT = "land_plot"
    COMMERCIAL = "commercial"
    HOTEL = "hotel"
    STUDIO = "studio"

class ListingType(str, Enum):
    RENT = "rent"
    SALE = "sale"
    LEASE = "lease"
    DAILY_RENT = "daily_rent"
    LEASEHOLD_MORTGAGE = "leasehold_mortgage"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Amenity schemas
class AmenityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)  # Georgian name (default)
    name_en: Optional[str] = Field(None, max_length=100)  # English name
    name_ru: Optional[str] = Field(None, max_length=100)  # Russian name
    description: Optional[str] = None  # Georgian description (default)
    description_en: Optional[str] = None  # English description
    description_ru: Optional[str] = None  # Russian description
    icon: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)

class AmenityCreate(AmenityBase):
    pass

class AmenityResponse(AmenityBase):
    id: int
    
    class Config:
        from_attributes = True

# Property Image schemas
class PropertyImageBase(BaseModel):
    image_url: str = Field(..., min_length=1, max_length=500)
    caption: Optional[str] = Field(None, max_length=255)
    is_primary: bool = False
    order_index: int = Field(default=0, ge=0)

class PropertyImageCreate(PropertyImageBase):
    pass

class PropertyImageUpdate(BaseModel):
    caption: Optional[str] = Field(None, max_length=255)
    is_primary: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)

class PropertyImageResponse(PropertyImageBase):
    id: int
    property_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Property schemas
class PropertyBase(BaseModel):
    title: str = Field(..., max_length=255)  # Georgian title (default)
    title_en: Optional[str] = Field(None, max_length=255)  # English title
    title_ru: Optional[str] = Field(None, max_length=255)  # Russian title
    description: Optional[str] = None  # Georgian description (default)
    description_en: Optional[str] = None  # English description
    description_ru: Optional[str] = None  # Russian description
    address: str = Field(..., max_length=500)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(..., max_length=100)
    property_type: str = Field(..., max_length=50)
    listing_type: str = Field(..., max_length=50)
    bedrooms: int = Field(...)
    bathrooms: float = Field(...)
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    rent_amount: float = Field(...)
    rent_amount_usd: Optional[float] = None
    security_deposit: Optional[float] = None
    lease_duration: int = Field(...)
    available_date: Optional[datetime] = None
    is_available: bool = Field(...)
    is_furnished: bool = Field(...)
    pets_allowed: bool = Field(...)
    smoking_allowed: bool = Field(...)
    year_built: Optional[int] = None
    parking_spaces: int = Field(...)
    utilities_included: Optional[str] = Field(None, max_length=500)
    district: Optional[str] = Field(None, max_length=100)
    urban_area: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    external_id: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=50)
    user_type: Optional[str] = Field(None, max_length=50)
    last_scraped: Optional[datetime] = None
    owner_id: int = Field(...)

class PropertyCreate(PropertyBase):
    amenity_ids: Optional[List[int]] = []

class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    title_en: Optional[str] = Field(None, max_length=255)
    title_ru: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    zip_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[float] = Field(None, ge=0)
    square_feet: Optional[int] = Field(None, ge=0)
    lot_size: Optional[float] = Field(None, ge=0)
    rent_amount: Optional[float] = Field(None, gt=0)
    security_deposit: Optional[float] = Field(None, ge=0)
    lease_duration: Optional[int] = Field(None, ge=1)
    available_date: Optional[datetime] = None
    is_available: Optional[bool] = None
    is_furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
    smoking_allowed: Optional[bool] = None
    year_built: Optional[int] = Field(None, ge=1800, le=2030)
    parking_spaces: Optional[int] = Field(None, ge=0)
    utilities_included: Optional[str] = None
    amenity_ids: Optional[List[int]] = None
    images: Optional[List[PropertyImageUpdate]] = None  # Add images field

class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    images: Optional[List[PropertyImageResponse]] = []
    amenities: Optional[List[AmenityResponse]] = []
    
    class Config:
        from_attributes = True

class PropertyListResponse(BaseModel):
    id: int
    title: str
    title_en: Optional[str] = None
    title_ru: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    address: str
    city: str
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str
    property_type: str
    listing_type: str
    bedrooms: int
    bathrooms: float
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    rent_amount: float
    rent_amount_usd: Optional[float] = None
    security_deposit: Optional[float] = None
    lease_duration: int
    available_date: Optional[datetime] = None
    is_available: bool
    is_furnished: bool
    pets_allowed: bool
    smoking_allowed: bool
    year_built: Optional[int] = None
    parking_spaces: int
    utilities_included: Optional[str] = None
    district: Optional[str] = None
    urban_area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    external_id: Optional[str] = None
    source: Optional[str] = None
    user_type: Optional[str] = None
    last_scraped: Optional[datetime] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Images (will be loaded via relationship)
    images: List["PropertyImageResponse"] = []
    amenities: Optional[List[AmenityResponse]] = []
    
    class Config:
        from_attributes = True

# Rental Application schemas
class RentalApplicationBase(BaseModel):
    move_in_date: datetime
    lease_duration: int = Field(..., ge=1)
    monthly_income: float = Field(..., gt=0)
    employment_status: str = Field(..., min_length=1, max_length=100)
    employer_name: Optional[str] = Field(None, max_length=255)
    employer_contact: Optional[str] = Field(None, max_length=500)
    references: Optional[str] = None  # JSON string
    pets: Optional[str] = None  # JSON string
    additional_notes: Optional[str] = None

class RentalApplicationCreate(RentalApplicationBase):
    property_id: int

class RentalApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    move_in_date: Optional[datetime] = None
    lease_duration: Optional[int] = Field(None, ge=1)
    monthly_income: Optional[float] = Field(None, gt=0)
    employment_status: Optional[str] = Field(None, min_length=1, max_length=100)
    employer_name: Optional[str] = Field(None, max_length=255)
    employer_contact: Optional[str] = Field(None, max_length=500)
    references: Optional[str] = None
    pets: Optional[str] = None
    additional_notes: Optional[str] = None

class RentalApplicationResponse(RentalApplicationBase):
    id: int
    property_id: int
    tenant_id: int
    status: ApplicationStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Search and filter schemas
class PropertySearchFilters(BaseModel):
    # Basic search
    query: Optional[str] = None  # General search query
    city: Optional[str] = None
    state: Optional[str] = None
    property_type: Optional[PropertyType] = None
    
    # Bedroom and bathroom filters
    min_bedrooms: Optional[int] = Field(None, ge=0)
    max_bedrooms: Optional[int] = Field(None, ge=0)
    min_bathrooms: Optional[float] = Field(None, ge=0)
    max_bathrooms: Optional[float] = Field(None, ge=0)
    
    # Price filters
    min_rent: Optional[float] = Field(None, ge=0)
    max_rent: Optional[float] = Field(None, ge=0)
    
    # Area filters
    min_square_feet: Optional[int] = Field(None, ge=0)
    max_square_feet: Optional[int] = Field(None, ge=0)
    
    # Property features
    pets_allowed: Optional[bool] = None
    is_furnished: Optional[bool] = None
    smoking_allowed: Optional[bool] = None
    
    # Amenities
    amenity_ids: Optional[List[int]] = []
    
    # Availability
    available_from: Optional[datetime] = None
    is_available: Optional[bool] = True  # Default to only available properties
    
    # Additional filters for frontend compatibility
    year_built_min: Optional[int] = Field(None, ge=1800, le=2030)
    year_built_max: Optional[int] = Field(None, ge=1800, le=2030)
    parking_spaces_min: Optional[int] = Field(None, ge=0)
    
    # Sort options
    sort_by: Optional[str] = Field(None, pattern="^(price|area|date|bedrooms)$")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$")

# Generic response schemas
class MessageResponse(BaseModel):
    message: str

class PaginationInfo(BaseModel):
    currentPage: int
    totalPages: int
    totalCount: int
    hasNext: bool
    hasPrev: bool

class PropertyPaginatedResponse(BaseModel):
    data: List[PropertyListResponse]
    pagination: PaginationInfo

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int
