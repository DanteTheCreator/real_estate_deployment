"""
Database service for property data persistence.
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, or_, func

# Add parent directories to path for Docker compatibility
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from database import (
        Property, PropertyParameter, Parameter, User, SessionLocal
    )
    # Import database models with aliases to avoid confusion
    from database import PropertyImage as DBPropertyImage
    from database import PropertyPrice as DBPropertyPrice
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('/app')
    from database import (
        Property, PropertyParameter, Parameter, User, SessionLocal
    )
    # Import database models with aliases to avoid confusion
    from database import PropertyImage as DBPropertyImage
    from database import PropertyPrice as DBPropertyPrice

from database import (
    Property, PropertyImage, PropertyParameter, PropertyPrice,
    Parameter, User, SessionLocal
)

# Import with fallbacks for Docker compatibility
try:
    from core.config import ScrapingConfig
    from models.property_data import PropertyData, PropertyPrice as DataPropertyPrice, PropertyParameter as DataPropertyParameter, PropertyImage as DataPropertyImage
except ImportError:
    try:
        from ..core.config import ScrapingConfig
        from ..models.property_data import PropertyData, PropertyPrice as DataPropertyPrice, PropertyParameter as DataPropertyParameter, PropertyImage as DataPropertyImage
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.models.property_data import PropertyData, PropertyPrice as DataPropertyPrice, PropertyParameter as DataPropertyParameter, PropertyImage as DataPropertyImage


class DatabaseService:
    """Service for handling database operations."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the database service."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return SessionLocal()
    
    def create_default_user(self, db: Session) -> User:
        """Create or get default system user."""
        try:
            default_user = db.query(User).filter(User.email == "system@scraper.com").first()
            
            if not default_user:
                default_user = User(
                    email="system@scraper.com",
                    first_name="System",
                    last_name="Scraper",
                    password_hash="dummy_hash",
                    role="admin",
                    is_active=True,
                    is_verified=True
                )
                db.add(default_user)
                db.commit()
                db.refresh(default_user)
                self.logger.info("Created default system user")
            
            return default_user
            
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Failed to create default user: {e}")
    
    def save_property(self, db: Session, property_data: PropertyData, default_user: User) -> Optional[Property]:
        """Save property data to database."""
        try:
            property_id = property_data.external_id
            self.logger.info(f"💾 Starting to save property {property_id} to database")
            
            # Prepare property data for database
            property_dict = property_data.to_dict()
            property_dict['owner_id'] = default_user.id
            
            # Log key values before saving
            self.logger.info(f"📊 Property {property_id} data before save:")
            self.logger.info(f"   - is_available: {property_dict.get('is_available')}")
            self.logger.info(f"   - bathrooms: {property_dict.get('bathrooms')}")
            self.logger.info(f"   - bedrooms: {property_dict.get('bedrooms')}")
            self.logger.info(f"   - listing_type: {property_dict.get('listing_type')}")
            self.logger.info(f"   - owner_id: {property_dict.get('owner_id')}")
            
            # Create property record
            property_obj = Property(**property_dict)
            db.add(property_obj)
            db.flush()  # Get the ID
            
            self.logger.debug(f"✅ Property {property_id} main record created with DB ID: {property_obj.id}")
            
            # Create parameter definitions first if we have raw parameter data
            if hasattr(property_data, 'raw_parameters') and property_data.raw_parameters:
                self.logger.info(f"🏗️ Creating parameter definitions for property {property_id}")
                for param_data in property_data.raw_parameters:
                    if isinstance(param_data, dict):
                        self._ensure_parameter_exists(db, param_data)
            
            # Add related records
            self.logger.info(f"📷 Saving {len(property_data.images)} images for property {property_id}")
            self._save_property_images(db, property_obj.id, property_data.images)
            
            self.logger.info(f"🏷️ Saving {len(property_data.parameters)} parameters for property {property_id}")
            self._save_property_parameters(db, property_obj.id, property_data.parameters)
            
            self.logger.info(f"💰 Saving {len(property_data.prices)} prices for property {property_id}")
            self._save_property_prices(db, property_obj.id, property_data.prices)
            
            db.commit()
            db.refresh(property_obj)
            
            # Log final values after save
            self.logger.info(f"✅ Property {property_id} saved successfully! Final values:")
            self.logger.info(f"   - DB ID: {property_obj.id}")
            self.logger.info(f"   - is_available: {property_obj.is_available}")
            self.logger.info(f"   - bathrooms: {property_obj.bathrooms}")
            self.logger.info(f"   - bedrooms: {property_obj.bedrooms}")
            
            return property_obj
            
        except IntegrityError as e:
            db.rollback()
            self.logger.warning(f"⚠️ Integrity error saving property {property_data.external_id}: {e}")
            return None
        except Exception as e:
            db.rollback()
            self.logger.error(f"❌ Error saving property {property_data.external_id}: {e}")
            raise RuntimeError(f"Failed to save property: {e}")
    
    def _save_property_images(self, db: Session, property_id: int, images: List) -> None:
        """Save property images."""
        for idx, image in enumerate(images):
            image_data = image.to_dict()
            image_data['property_id'] = property_id
            
            # Use the database model class (DBPropertyImage, not PropertyImage)
            property_image = DBPropertyImage(**image_data)
            db.add(property_image)
    
    def _save_property_parameters(self, db: Session, property_id: int, parameters: List) -> None:
        """Save property parameters."""
        for param in parameters:
            # Map external_id to internal parameter ID
            parameter_external_id = param.parameter_id  # This contains the external_id from API
            
            # Find the parameter by external_id and get its internal id
            existing_param = db.query(Parameter).filter(Parameter.external_id == parameter_external_id).first()
            
            if not existing_param:
                self.logger.info(f"Creating new parameter with external_id: {parameter_external_id}")
                # Create basic parameter record if it doesn't exist
                existing_param = Parameter(
                    external_id=parameter_external_id,
                    key=f'param_{parameter_external_id}',
                    sort_index=parameter_external_id,
                    parameter_type='parameter',
                    display_name=f'Parameter {parameter_external_id}'
                )
                db.add(existing_param)
                db.flush()  # Get the ID
            
            # Create PropertyParameter with the correct internal parameter ID
            property_param = PropertyParameter(
                property_id=property_id,
                parameter_id=existing_param.id,  # Use the internal database ID
                parameter_value=param.parameter_value,
                parameter_select_name=param.parameter_select_name
            )
            db.add(property_param)
    
    def _save_property_prices(self, db: Session, property_id: int, prices: List) -> None:
        """Save property prices."""
        for idx, price in enumerate(prices):
            price_data = price.to_dict()
            price_data['property_id'] = property_id
            
            # Use the database model class (DBPropertyPrice, not PropertyPrice)
            property_price = DBPropertyPrice(**price_data)
            db.add(property_price)
    
    def _ensure_parameter_exists(self, db: Session, param_data: dict) -> Parameter:
        """Ensure parameter exists in database with full API data."""
        external_id = param_data.get('id')
        existing_param = db.query(Parameter).filter(Parameter.external_id == external_id).first()
        
        if not existing_param:
            # Create parameter record with full API data
            parameter = Parameter(
                external_id=external_id,
                key=param_data.get('key', f'param_{external_id}'),
                sort_index=param_data.get('sort_index', 0),
                deal_type_id=param_data.get('deal_type_id'),
                input_name=param_data.get('input_name'),
                select_name=param_data.get('select_name'),
                svg_file_name=param_data.get('svg_file_name'),
                background_color=param_data.get('background_color'),
                parameter_type=param_data.get('type', 'parameter'),
                display_name=param_data.get('display_name', f'Parameter {external_id}'),
                display_name_en=None,  # TODO: Add if multilingual support needed
                display_name_ru=None   # TODO: Add if multilingual support needed
            )
            db.add(parameter)
            db.flush()
            self.logger.info(f"Created parameter: {parameter.key} ({parameter.display_name})")
            return parameter
        
        return existing_param
    
    def find_existing_property(self, db: Session, external_id: str) -> Optional[Property]:
        """Find existing property by external ID."""
        return db.query(Property).filter(
            Property.external_id == external_id,
            Property.source == 'myhome.ge'
        ).first()
    
    def update_property(self, db: Session, existing_property: Property, 
                       property_data: PropertyData) -> Property:
        """Update existing property with new data."""
        try:
            # Update basic fields
            property_dict = property_data.to_dict()
            for key, value in property_dict.items():
                if hasattr(existing_property, key):
                    setattr(existing_property, key, value)
            
            # Update timestamp
            existing_property.updated_at = datetime.now()
            existing_property.last_scraped = datetime.now()
            
            # Remove old related records manually to avoid foreign key issues
            try:
                db.query(PropertyImage).filter(PropertyImage.property_id == existing_property.id).delete()
                db.query(PropertyParameter).filter(PropertyParameter.property_id == existing_property.id).delete()
                db.query(PropertyPrice).filter(PropertyPrice.property_id == existing_property.id).delete()
                db.flush()  # Flush deletions
            except Exception as e:
                self.logger.warning(f"Error deleting old related records for property {property_data.external_id}: {e}")
            
            # Add new related records
            self._save_property_images(db, existing_property.id, property_data.images)
            self._save_property_parameters(db, existing_property.id, property_data.parameters)
            self._save_property_prices(db, existing_property.id, property_data.prices)
            
            db.commit()
            db.refresh(existing_property)
            
            self.logger.debug(f"Successfully updated property {property_data.external_id}")
            return existing_property
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating property {property_data.external_id}: {e}")
            raise RuntimeError(f"Failed to update property: {e}")
    
    def cleanup_old_properties(self, db: Session) -> int:
        """Remove properties that haven't been scraped recently."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.cleanup_days)
            
            old_properties = db.query(Property).filter(
                and_(
                    Property.source == 'myhome.ge',
                    or_(
                        Property.last_scraped < cutoff_date,
                        Property.last_scraped.is_(None)
                    )
                )
            ).all()
            
            count = len(old_properties)
            if count > 0:
                # Delete properties one by one to ensure cascading works properly
                for prop in old_properties:
                    try:
                        # Manually delete related records first if cascade doesn't work
                        db.query(PropertyImage).filter(PropertyImage.property_id == prop.id).delete()
                        db.query(PropertyParameter).filter(PropertyParameter.property_id == prop.id).delete()
                        db.query(PropertyPrice).filter(PropertyPrice.property_id == prop.id).delete()
                        
                        # Now delete the property
                        db.delete(prop)
                        db.flush()  # Flush each delete to catch issues early
                        
                    except Exception as e:
                        self.logger.warning(f"Error deleting property {prop.id}: {e}")
                        db.rollback()
                        continue
                
                db.commit()
                self.logger.info(f"Cleaned up {count} old properties")
            
            return count
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error cleaning up old properties: {e}")
            return 0
    
    def get_active_property_ids(self, db: Session) -> List[str]:
        """Get list of active property external IDs."""
        try:
            properties = db.query(Property.external_id).filter(
                Property.source == 'myhome.ge',
                Property.is_available == True
            ).all()
            
            return [prop.external_id for prop in properties]
            
        except Exception as e:
            self.logger.error(f"Error getting active property IDs: {e}")
            return []
    
    def get_property_count(self, db: Session) -> int:
        """Get total count of properties."""
        try:
            return db.query(Property).filter(Property.source == 'myhome.ge').count()
        except Exception as e:
            self.logger.error(f"Error getting property count: {e}")
            return 0
