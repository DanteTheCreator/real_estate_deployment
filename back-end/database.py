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

# Association table for property amenities (many-to-many)
property_amenities = Table(
    'property_amenities',
    Base.metadata,
    Column('property_id', Integer, ForeignKey('properties.id'), primary_key=True),
    Column('amenity_id', Integer, ForeignKey('amenities.id'), primary_key=True)
)

# Association table for saved properties (many-to-many)
saved_properties = Table(
    'saved_properties',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('property_id', Integer, ForeignKey('properties.id'), primary_key=True),
    Column('saved_at', DateTime(timezone=True), server_default=func.now())
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
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(500))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    zip_code: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(100), default="USA")
    
    # Property details
    property_type: Mapped[str] = mapped_column(String(50))  # apartment, house, condo, etc.
    listing_type: Mapped[str] = mapped_column(String(50), default="rent")  # rent, sale, lease, daily, mortgage
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    square_feet: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lot_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Rental details
    rent_amount: Mapped[float] = mapped_column(Float)
    security_deposit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lease_duration: Mapped[int] = mapped_column(Integer, default=12)  # months
    available_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_furnished: Mapped[bool] = mapped_column(Boolean, default=False)
    pets_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    smoking_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Additional info
    year_built: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parking_spaces: Mapped[int] = mapped_column(Integer, default=0)
    utilities_included: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON string of included utilities
    
    # Location details (for scraped properties)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # District name
    urban_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Urban/neighborhood name
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floor_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Scraper metadata
    external_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # Original ID from external source
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Source of the listing (e.g., 'myhome.ge')
    user_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'physical' for owner, 'agent' for agent
    last_scraped: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="properties")
    amenities: Mapped[List["Amenity"]] = relationship("Amenity", secondary=property_amenities, back_populates="properties")
    applications: Mapped[List["RentalApplication"]] = relationship("RentalApplication", back_populates="property")
    images: Mapped[List["PropertyImage"]] = relationship("PropertyImage", back_populates="property")
    saved_by_users: Mapped[List["User"]] = relationship(
        "User", 
        secondary=saved_properties, 
        back_populates="saved_properties"
    )

class Amenity(Base):
    __tablename__ = "amenities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon name for frontend
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "utilities", "recreation", "appliances"
    
    # Relationships
    properties: Mapped[List["Property"]] = relationship("Property", secondary=property_amenities, back_populates="amenities")

class PropertyImage(Base):
    __tablename__ = "property_images"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    image_url: Mapped[str] = mapped_column(String(500))
    caption: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
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
