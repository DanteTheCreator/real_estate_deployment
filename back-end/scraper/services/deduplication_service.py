"""
Deduplication service for identifying and handling duplicate properties.
"""

import logging
import re
import sys
import os
from difflib import SequenceMatcher
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

# Add parent directories to path for Docker compatibility
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from database import Property
except ImportError:
    # Fallback for direct execution
    sys.path.append('/app')
    from database import Property

# Import with fallbacks for Docker compatibility
try:
    from core.config import ScrapingConfig
    from models.property_data import PropertyData
except ImportError:
    try:
        from ..core.config import ScrapingConfig
        from ..models.property_data import PropertyData
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.models.property_data import PropertyData


class DeduplicationService:
    """Service for handling property deduplication."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the deduplication service."""
        self.config = config
        self.enable_owner_priority = config.enable_owner_priority
        self.similarity_threshold = 0.85
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def find_duplicates(self, db: Session, property_data: PropertyData) -> List[Property]:
        """Find potential duplicate properties in the database."""
        property_id = property_data.external_id
        self.logger.info(f"🔍 Checking for duplicates of property {property_id}")
        duplicates = []
        
        try:
            # Primary check: exact external_id match
            exact_match = self._find_exact_match(db, property_data.external_id)
            if exact_match:
                self.logger.info(f"🎯 Found EXACT MATCH for property {property_id}: DB ID {exact_match.id}")
                duplicates.append(exact_match)
                return duplicates
            else:
                pass  # No exact match found
            
            # Secondary check: coordinate-based matching
            if property_data.latitude and property_data.longitude:
                coordinate_matches = self._find_coordinate_matches(
                    db, property_data.latitude, property_data.longitude
                )
                if coordinate_matches:
                    self.logger.info(f"📍 Found {len(coordinate_matches)} coordinate matches for property {property_id}")
                duplicates.extend(coordinate_matches)
            
            # Tertiary check: address similarity
            if property_data.address:
                address_matches = self._find_address_matches(db, property_data.address, duplicates)
                if address_matches:
                    self.logger.info(f"🏠 Found {len(address_matches)} address matches for property {property_id}")
                duplicates.extend(address_matches)
            
            if duplicates:
                self.logger.info(f"🔄 Total duplicates found for property {property_id}: {len(duplicates)}")
            else:
                self.logger.info(f"🆕 No duplicates found for property {property_id} - will be processed as NEW")
            
            return duplicates
            
        except Exception as e:
            self.logger.error(f"❌ Error finding duplicates for property {property_id}: {e}")
            return []
    
    def _find_exact_match(self, db: Session, external_id: str) -> Optional[Property]:
        """Find exact match by external ID."""
        self.logger.debug(f"🔍 Searching for exact match with external_id: {external_id}")
        result = db.query(Property).filter(
            Property.external_id == external_id,
            Property.source == 'myhome.ge'
        ).first()
        
        if result:
            self.logger.info(f"✅ Found exact match: external_id {external_id} -> DB ID {result.id}")
        else:
            self.logger.debug(f"❌ No exact match found for external_id: {external_id}")
        
        return result
    
    def _find_coordinate_matches(self, db: Session, lat: float, lng: float) -> List[Property]:
        """Find properties with very similar coordinates."""
        coordinate_tolerance = 0.0001  # Approximately 10 meters
        
        return db.query(Property).filter(
            and_(
                Property.latitude.isnot(None),
                Property.longitude.isnot(None),
                func.abs(Property.latitude - lat) < coordinate_tolerance,
                func.abs(Property.longitude - lng) < coordinate_tolerance,
                Property.source == 'myhome.ge'
            )
        ).all()
    
    def _find_address_matches(self, db: Session, address: str, 
                            exclude_properties: List[Property]) -> List[Property]:
        """Find properties with similar addresses."""
        exclude_ids = [prop.id for prop in exclude_properties]
        
        # Get all properties from the same source
        all_properties = db.query(Property).filter(
            Property.source == 'myhome.ge'
        )
        
        if exclude_ids:
            all_properties = all_properties.filter(~Property.id.in_(exclude_ids))
        
        all_properties = all_properties.all()
        
        similar_properties = []
        for prop in all_properties:
            if prop.address:
                similarity = self._calculate_address_similarity(address, prop.address)
                if similarity >= self.similarity_threshold:
                    similar_properties.append(prop)
        
        return similar_properties
    
    def _calculate_address_similarity(self, addr1: str, addr2: str) -> float:
        """Calculate similarity between two addresses."""
        if not addr1 or not addr2:
            return 0.0
        
        # Normalize addresses
        addr1_norm = self._normalize_address(addr1)
        addr2_norm = self._normalize_address(addr2)
        
        return SequenceMatcher(None, addr1_norm, addr2_norm).ratio()
    
    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison."""
        # Convert to lowercase
        normalized = address.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common punctuation
        normalized = re.sub(r'[.,;:!?-]', '', normalized)
        
        # Remove common address variations
        replacements = {
            'street': 'str',
            'avenue': 'ave',
            'boulevard': 'blvd',
            'квартира': 'кв',
            'apartment': 'apt'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def should_replace_duplicate(self, new_property: PropertyData, 
                               existing_property: Property) -> bool:
        """Determine if new property should replace existing one."""
        if not self.enable_owner_priority:
            return False
        
        new_is_owner = new_property.user_type == 'owner'
        existing_is_owner = existing_property.user_type == 'owner'
        
        # Priority rules:
        # 1. Owner listing replaces agency listing
        if new_is_owner and not existing_is_owner:
            self.logger.info(f"Owner listing replaces agency listing for {new_property.external_id}")
            return True
        
        # 2. If both are owners or both are agencies, keep existing (first come, first served)
        if new_is_owner == existing_is_owner:
            return False
        
        # 3. Agency listing doesn't replace owner listing
        return False
    
    def is_owner_listing(self, property_data: PropertyData) -> bool:
        """Determine if a listing is from property owner."""
        return property_data.user_type == 'owner'
    
    def get_deduplication_stats(self, total_processed: int, duplicates_found: int, 
                              owner_prioritized: int, agency_discarded: int) -> dict:
        """Get deduplication statistics."""
        return {
            'total_processed': total_processed,
            'duplicates_found': duplicates_found,
            'owner_prioritized': owner_prioritized,
            'agency_discarded': agency_discarded,
            'duplicate_rate': (duplicates_found / max(total_processed, 1)) * 100,
            'owner_priority_enabled': self.enable_owner_priority
        }
