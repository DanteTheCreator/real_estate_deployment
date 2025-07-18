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
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    STUDIO = "studio"

class ListingType(str, Enum):
    RENT = "rent"
    SALE = "sale"
    LEASE = "lease"
    DAILY = "daily"
    MORTGAGE = "mortgage"

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
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
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
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zip_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="USA", max_length=100)
    property_type: PropertyType
    listing_type: ListingType = ListingType.RENT
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0)
    square_feet: Optional[int] = Field(None, ge=0)
    lot_size: Optional[float] = Field(None, ge=0)
    rent_amount: float = Field(..., gt=0)
    security_deposit: Optional[float] = Field(None, ge=0)
    lease_duration: int = Field(default=12, ge=1)
    available_date: Optional[datetime] = None
    is_furnished: bool = False
    pets_allowed: bool = False
    smoking_allowed: bool = False
    year_built: Optional[int] = Field(None, ge=1800, le=2030)
    parking_spaces: int = Field(default=0, ge=0)
    utilities_included: Optional[str] = None

class PropertyCreate(PropertyBase):
    amenity_ids: Optional[List[int]] = []

class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
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
    is_available: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    images: Optional[List[PropertyImageResponse]] = []
    amenities: Optional[List[AmenityResponse]] = []
    
    class Config:
        from_attributes = True

class PropertyListResponse(BaseModel):
    id: int
    title: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: PropertyType
    bedrooms: int
    bathrooms: float
    rent_amount: float
    is_available: bool
    created_at: datetime
    images: Optional[List[PropertyImageResponse]] = []
    
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

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int
