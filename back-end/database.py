from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
from config import settings

# Create engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Association table for saved properties (many-to-many)
saved_properties = Table(
    'saved_properties',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('property_id', Integer, ForeignKey('properties.id'), primary_key=True),
    Column('saved_at', DateTime(timezone=True), server_default=func.now())
)

# Association table for property amenities (many-to-many)
property_amenities = Table(
    'property_amenities',
    Base.metadata,
    Column('property_id', Integer, ForeignKey('properties.id'), primary_key=True),
    Column('amenity_id', Integer, ForeignKey('amenities.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user")  # user, admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    properties: Mapped[List["Property"]] = relationship("Property", back_populates="owner")
    applications: Mapped[List["RentalApplication"]] = relationship("RentalApplication", back_populates="tenant")
    saved_properties: Mapped[List["Property"]] = relationship(
        "Property", 
        secondary=saved_properties, 
        back_populates="saved_by_users"
    )

class Property(Base):
    __tablename__ = "properties"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))  # Georgian title (default)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # English title
    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Russian title
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Georgian description (default)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # English description
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Russian description
    address: Mapped[str] = mapped_column(String(500))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    zip_code: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(100))
    property_type: Mapped[str] = mapped_column(String(50))
    listing_type: Mapped[str] = mapped_column(String(50))
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    square_feet: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lot_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rent_amount: Mapped[float] = mapped_column(Float)
    rent_amount_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    security_deposit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lease_duration: Mapped[int] = mapped_column(Integer)  # months
    available_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_furnished: Mapped[bool] = mapped_column(Boolean, default=False)
    pets_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    smoking_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    year_built: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parking_spaces: Mapped[int] = mapped_column(Integer, default=0)
    utilities_included: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    urban_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floor_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_scraped: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="properties")
    parameters: Mapped[List["PropertyParameter"]] = relationship("PropertyParameter", back_populates="property", cascade="all, delete-orphan")
    prices: Mapped[List["PropertyPrice"]] = relationship("PropertyPrice", back_populates="property", cascade="all, delete-orphan")
    applications: Mapped[List["RentalApplication"]] = relationship("RentalApplication", back_populates="property")
    images: Mapped[List["PropertyImage"]] = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    amenities: Mapped[List["Amenity"]] = relationship(
        "Amenity",
        secondary=property_amenities,
        back_populates="properties"
    )
    saved_by_users: Mapped[List["User"]] = relationship(
        "User", 
        secondary=saved_properties, 
        back_populates="saved_properties"
    )

class Amenity(Base):
    __tablename__ = "amenities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)  # Georgian name (default)
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # English name
    name_ru: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Russian name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Georgian description (default)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # English description
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Russian description
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon name for frontend
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "utilities", "recreation", "appliances"
    
    # Relationships
    properties: Mapped[List["Property"]] = relationship(
        "Property",
        secondary=property_amenities,
        back_populates="amenities"
    )

class Parameter(Base):
    __tablename__ = "parameters"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)  # ID from external API
    key: Mapped[str] = mapped_column(String(100), index=True)
    sort_index: Mapped[int] = mapped_column(Integer)
    deal_type_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    input_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    select_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    svg_file_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    background_color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    parameter_type: Mapped[str] = mapped_column(String(50))  # 'parameter', 'feature', 'furniture-equipment', 'label'
    display_name: Mapped[str] = mapped_column(String(200))  # Georgian display name (default)
    display_name_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # English display name
    display_name_ru: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Russian display name
    
    # Relationships
    property_parameters: Mapped[List["PropertyParameter"]] = relationship("PropertyParameter", back_populates="parameter")

class PropertyParameter(Base):
    __tablename__ = "property_parameters"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    parameter_id: Mapped[int] = mapped_column(ForeignKey("parameters.id"))
    parameter_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # For parameters with values
    parameter_select_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="parameters")
    parameter: Mapped["Parameter"] = relationship("Parameter", back_populates="property_parameters")

class PropertyPrice(Base):
    __tablename__ = "property_prices"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    currency_type: Mapped[str] = mapped_column(String(10))  # '1' for USD, '2' for GEL, '3' for EUR
    price_total: Mapped[float] = mapped_column(Float)
    price_square: Mapped[float] = mapped_column(Float)  # Price per square meter
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="prices")

class PropertyImage(Base):
    __tablename__ = "property_images"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    image_url: Mapped[str] = mapped_column(String(500))  # Image URL
    caption: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Image caption
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)  # Primary image flag
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="images")

class RentalApplication(Base):
    __tablename__ = "rental_applications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    tenant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Application details
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected, withdrawn
    move_in_date: Mapped[datetime] = mapped_column(DateTime)
    lease_duration: Mapped[int] = mapped_column(Integer)  # months
    monthly_income: Mapped[float] = mapped_column(Float)
    employment_status: Mapped[str] = mapped_column(String(100))
    employer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employer_contact: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Personal references
    references: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of references
    
    # Additional info
    pets: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of pet information
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="applications")
    tenant: Mapped["User"] = relationship("User", back_populates="applications")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
