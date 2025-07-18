#!/usr/bin/env python3
"""
Database integration module for the property scraper
Maps scraped property data to the backend database schema
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Add backend directory to path to import database models
backend_path = Path(__file__).parent.parent / "back-end"
sys.path.append(str(backend_path))

from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Import backend models and config
try:
    from database import Base, User, Property, PropertyImage, get_db
    from config import settings
except ImportError as e:
    logging.error(f"Failed to import backend modules: {e}")
    logging.error("Make sure the backend directory is accessible and dependencies are installed")
    sys.exit(1)

# Import scraper classes
from enhanced_scraper import Property as ScrapedProperty

logger = logging.getLogger(__name__)

class DatabaseIntegrator:
    """Handles integration between scraped properties and backend database"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection"""
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create a default system user for scraped properties if it doesn't exist
        self.system_user_id = self._ensure_system_user()
    
    def _ensure_system_user(self) -> int:
        """Ensure a system user exists for scraped properties"""
        with self.SessionLocal() as db:
            # Check if system user exists
            system_user = db.query(User).filter(User.email == "system@scraper.internal").first()
            
            if not system_user:
                # Create system user
                system_user = User(
                    email="system@scraper.internal",
                    password_hash="no_login",  # System user cannot login
                    first_name="System",
                    last_name="Scraper",
                    role="system",
                    is_active=True,
                    is_verified=True
                )
                db.add(system_user)
                db.commit()
                db.refresh(system_user)
                logger.info(f"Created system user with ID: {system_user.id}")
            
            return system_user.id
    
    def _map_deal_type(self, deal_type_id: int) -> str:
        """Map deal type ID to listing type string"""
        deal_type_mapping = {
            1: "rent",      # Rental
            2: "sale",      # Sale
            3: "lease",     # Long-term lease
            4: "daily",     # Daily rental
            5: "mortgage"   # Mortgage
        }
        return deal_type_mapping.get(deal_type_id, "rent")
    
    def _map_property_type(self, real_estate_type_id: int) -> str:
        """Map real estate type ID to property type string"""
        property_type_mapping = {
            1: "apartment",
            2: "house", 
            3: "condo",
            4: "office",
            5: "commercial",
            6: "land",
            7: "warehouse",
            8: "hotel"
        }
        return property_type_mapping.get(real_estate_type_id, "apartment")
    
    def _parse_rooms_and_bedrooms(self, room_str: str, bedroom_str: str) -> tuple[int, float]:
        """Parse room and bedroom strings to numbers"""
        try:
            # Handle room count
            if room_str.isdigit():
                bedrooms = int(room_str)
            else:
                bedrooms = 1  # Default
            
            # Handle bathroom count (often same as bedroom for simplicity)
            if bedroom_str.isdigit():
                bathrooms = float(bedroom_str)
            else:
                bathrooms = 1.0  # Default
                
        except (ValueError, AttributeError):
            bedrooms = 1
            bathrooms = 1.0
        
        return bedrooms, bathrooms
    
    def _extract_location_info(self, scraped_prop: ScrapedProperty) -> Dict[str, str]:
        """Extract and format location information"""
        # For Georgian properties, we'll use city_name as city
        # and create a formatted address
        
        address_parts = []
        if scraped_prop.district_name:
            address_parts.append(scraped_prop.district_name)
        if scraped_prop.urban_name:
            address_parts.append(scraped_prop.urban_name)
        if scraped_prop.address:
            address_parts.append(scraped_prop.address)
        
        formatted_address = ", ".join(filter(None, address_parts))
        
        return {
            "address": formatted_address or "Address not specified",
            "city": scraped_prop.city_name or "Tbilisi",
            "state": "Tbilisi",  # Default for Georgia
            "zip_code": "0000",   # Default
            "country": "Georgia"
        }
    
    def scraped_to_db_property(self, scraped_prop: ScrapedProperty) -> Property:
        """Convert scraped property to database property model"""
        
        # Parse rooms and bedrooms
        bedrooms, bathrooms = self._parse_rooms_and_bedrooms(
            scraped_prop.room, scraped_prop.bedroom
        )
        
        # Extract location info
        location_info = self._extract_location_info(scraped_prop)
        
        # Map property and deal types
        property_type = self._map_property_type(scraped_prop.real_estate_type_id)
        listing_type = self._map_deal_type(scraped_prop.deal_type_id)
        
        # Create property title from available info
        title_parts = []
        if scraped_prop.room:
            title_parts.append(f"{scraped_prop.room} rooms")
        if scraped_prop.area:
            title_parts.append(f"{scraped_prop.area}m²")
        if scraped_prop.district_name:
            title_parts.append(scraped_prop.district_name)
        
        title = " - ".join(title_parts) if title_parts else f"Property #{scraped_prop.id}"
        
        # Parse available date from last_updated
        available_date = None
        last_scraped = datetime.now()
        if scraped_prop.last_updated:
            try:
                available_date = datetime.fromisoformat(scraped_prop.last_updated.replace('Z', '+00:00'))
                last_scraped = available_date
            except ValueError:
                available_date = datetime.now()
        
        # Create database property
        db_property = Property(
            title=title,
            description=scraped_prop.comment or f"Property in {scraped_prop.district_name or 'Tbilisi'}",
            address=location_info["address"],
            city=location_info["city"],
            state=location_info["state"],
            zip_code=location_info["zip_code"],
            country=location_info["country"],
            
            # Property details
            property_type=property_type,
            listing_type=listing_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_feet=int(scraped_prop.area * 10.764) if scraped_prop.area else None,  # Convert m² to sq ft
            
            # Rental details
            rent_amount=float(scraped_prop.price_total),
            security_deposit=float(scraped_prop.price_total * 0.1) if scraped_prop.price_total > 0 else None,  # 10% default
            lease_duration=12,  # Default 12 months
            available_date=available_date,
            is_available=True,
            is_furnished=False,  # Default
            pets_allowed=False,  # Default
            smoking_allowed=False,  # Default
            
            # Additional info
            year_built=None,
            parking_spaces=0,  # Default
            utilities_included=None,
            
            # Location details (new fields)
            district=scraped_prop.district_name,
            urban_area=scraped_prop.urban_name,
            latitude=scraped_prop.lat if scraped_prop.lat != 0 else None,
            longitude=scraped_prop.lng if scraped_prop.lng != 0 else None,
            floor_number=scraped_prop.floor if scraped_prop.floor != 0 else None,
            total_floors=scraped_prop.total_floors if scraped_prop.total_floors != 0 else None,
            
            # Scraper metadata (new fields)
            external_id=str(scraped_prop.id),
            source="myhome.ge",
            user_type=scraped_prop.user_type,
            last_scraped=last_scraped,
            
            # Foreign keys
            owner_id=self.system_user_id,
        )
        
        return db_property
    
    def save_properties_to_db(self, scraped_properties: List[ScrapedProperty], 
                            batch_size: int = 100, 
                            skip_existing: bool = True) -> Dict[str, int]:
        """
        Save scraped properties to database
        
        Args:
            scraped_properties: List of scraped properties
            batch_size: Number of properties to process in each batch
            skip_existing: Whether to skip properties that already exist
            
        Returns:
            Dictionary with statistics about the save operation
        """
        stats = {
            "total_processed": 0,
            "saved": 0,
            "skipped": 0,
            "errors": 0
        }
        
        logger.info(f"Starting to save {len(scraped_properties)} properties to database")
        
        with self.SessionLocal() as db:
            for i in range(0, len(scraped_properties), batch_size):
                batch = scraped_properties[i:i + batch_size]
                batch_stats = self._save_property_batch(db, batch, skip_existing)
                
                # Update overall stats
                for key in stats:
                    stats[key] += batch_stats[key]
                
                logger.info(f"Processed batch {i//batch_size + 1}: "
                           f"saved={batch_stats['saved']}, "
                           f"skipped={batch_stats['skipped']}, "
                           f"errors={batch_stats['errors']}")
        
        logger.info(f"Finished saving properties. Stats: {stats}")
        return stats
    
    def _save_property_batch(self, db: Session, batch: List[ScrapedProperty], 
                           skip_existing: bool) -> Dict[str, int]:
        """Save a batch of properties to database"""
        batch_stats = {
            "total_processed": len(batch),
            "saved": 0,
            "skipped": 0,
            "errors": 0
        }
        
        for scraped_prop in batch:
            try:
                # Check if property already exists using multiple methods
                if skip_existing:
                    existing_property = self._find_existing_property(db, scraped_prop)
                    
                    if existing_property:
                        # Update last_scraped timestamp for existing property
                        existing_property.last_scraped = datetime.now()
                        db.commit()
                        batch_stats["skipped"] += 1
                        logger.debug(f"Skipped existing property with external_id: {scraped_prop.id}")
                        continue
                
                # Convert and save property
                db_property = self.scraped_to_db_property(scraped_prop)
                db.add(db_property)
                db.commit()
                
                batch_stats["saved"] += 1
                logger.debug(f"Saved new property with external_id: {scraped_prop.id}")
                
            except SQLAlchemyError as e:
                logger.error(f"Database error saving property {scraped_prop.id}: {e}")
                db.rollback()
                batch_stats["errors"] += 1
                
            except Exception as e:
                logger.error(f"Unexpected error saving property {scraped_prop.id}: {e}")
                db.rollback()
                batch_stats["errors"] += 1
        
        return batch_stats
    
    def _find_existing_property(self, db: Session, scraped_prop: ScrapedProperty) -> Optional[Property]:
        """
        Find existing property using multiple detection methods:
        1. By external_id (most reliable)
        2. By address + area + price (fuzzy matching)
        3. By coordinates + area (location-based matching)
        """
        
        # Method 1: Check by external_id (most reliable)
        existing = db.query(Property).filter(
            Property.external_id == str(scraped_prop.id),
            Property.source == "myhome.ge"
        ).first()
        
        if existing:
            return existing
        
        # Method 2: Check by address + area + price
        location_info = self._extract_location_info(scraped_prop)
        
        # Normalize address for comparison
        normalized_address = location_info["address"].lower().strip()
        
        # Find properties with similar address, area, and price
        similar_properties = db.query(Property).filter(
            Property.rent_amount == float(scraped_prop.price_total)
        ).all()
        
        for prop in similar_properties:
            prop_address = prop.address.lower().strip()
            
            # Check if addresses are very similar (allow for small differences)
            if self._addresses_match(normalized_address, prop_address) and \
               self._areas_match(scraped_prop.area, prop.square_feet) and \
               self._locations_match(scraped_prop, prop):
                return prop
        
        # Method 3: Check by coordinates + area (for properties with GPS data)
        if scraped_prop.lat and scraped_prop.lng and scraped_prop.lat != 0 and scraped_prop.lng != 0:
            # Find properties within 100 meters with similar area
            lat_tolerance = 0.001  # approximately 100 meters
            lng_tolerance = 0.001
            
            nearby_properties = db.query(Property).filter(
                Property.latitude.between(scraped_prop.lat - lat_tolerance, scraped_prop.lat + lat_tolerance),
                Property.longitude.between(scraped_prop.lng - lng_tolerance, scraped_prop.lng + lng_tolerance)
            ).all()
            
            for prop in nearby_properties:
                if self._areas_match(scraped_prop.area, prop.square_feet) and \
                   abs(prop.rent_amount - scraped_prop.price_total) < (scraped_prop.price_total * 0.1):  # 10% price tolerance
                    return prop
        
        return None
    
    def _addresses_match(self, addr1: str, addr2: str) -> bool:
        """Check if two addresses are likely the same"""
        # Remove common words and punctuation for comparison
        import re
        
        def normalize_address(addr):
            # Remove numbers, punctuation, and common words
            addr = re.sub(r'[0-9.,;:\-\s]+', ' ', addr)
            addr = re.sub(r'\b(street|st|avenue|ave|road|rd|district|area)\b', '', addr)
            return ' '.join(addr.split()).lower()
        
        norm_addr1 = normalize_address(addr1)
        norm_addr2 = normalize_address(addr2)
        
        # Check if one address contains the other (for similar but not identical addresses)
        return norm_addr1 in norm_addr2 or norm_addr2 in norm_addr1
    
    def _areas_match(self, area_m2: Optional[int], square_feet: Optional[int]) -> bool:
        """Check if areas match (allowing for conversion and tolerance)"""
        if not area_m2 or not square_feet:
            return True  # If we don't have area data, don't use it for matching
        
        # Convert m² to sq ft
        area_sq_ft = area_m2 * 10.764
        
        # Allow 10% tolerance
        tolerance = 0.1
        return abs(area_sq_ft - square_feet) < (square_feet * tolerance)
    
    def _locations_match(self, scraped_prop: ScrapedProperty, db_prop: Property) -> bool:
        """Check if locations match (district, urban area)"""
        # Check district match
        if scraped_prop.district_name and db_prop.district:
            if scraped_prop.district_name.lower() != db_prop.district.lower():
                return False
        
        # Check urban area match
        if scraped_prop.urban_name and db_prop.urban_area:
            if scraped_prop.urban_name.lower() != db_prop.urban_area.lower():
                return False
        
        return True
    
    def get_property_count(self) -> int:
        """Get total count of properties in database"""
        with self.SessionLocal() as db:
            return db.query(Property).count()
    
    def cleanup_system_properties(self) -> int:
        """Remove all properties created by the system user (for testing)"""
        with self.SessionLocal() as db:
            deleted_count = db.query(Property).filter(
                Property.owner_id == self.system_user_id
            ).delete()
            db.commit()
            logger.info(f"Deleted {deleted_count} system properties")
            return deleted_count

def test_database_connection():
    """Test database connection and setup"""
    try:
        integrator = DatabaseIntegrator()
        count = integrator.get_property_count()
        logger.info(f"Database connection successful. Current property count: {count}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test the database integration
    logging.basicConfig(level=logging.INFO)
    
    if test_database_connection():
        print("✅ Database integration is working!")
    else:
        print("❌ Database integration failed!")
