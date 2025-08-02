"""
Base data processor for converting API responses to structured data.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

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


class DataProcessor:
    """Handles property data processing and normalization."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the data processor."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_property(self, raw_data: Dict) -> Optional[PropertyData]:
        """Convert raw property data to PropertyData object."""
        try:
            property_id = raw_data.get('id', 'unknown')
            self.logger.info(f"🏠 Starting to process property {property_id}")
            
            # Create PropertyData instance with basic info
            basic_info = self._process_basic_info(raw_data)
            property_data = PropertyData(**basic_info)
            
            # Process different aspects of the property
            self._process_location(property_data, raw_data)
            self._process_property_details(property_data, raw_data)
            self._process_basic_financial(property_data, raw_data)
            self._process_features(property_data, raw_data)
            self._process_building_details(property_data, raw_data)
            
            # Set user type (owner vs agency)
            user_type = self._determine_user_type(raw_data)
            property_data.user_type = user_type
            
            # Final logging of key values
            self.logger.info(f"✅ Property {property_id} processed successfully:")
            self.logger.info(f"   - is_available: {property_data.is_available}")
            self.logger.info(f"   - bathrooms: {property_data.bathrooms}")
            self.logger.info(f"   - bedrooms: {property_data.bedrooms}")
            self.logger.info(f"   - listing_type: {property_data.listing_type}")
            self.logger.info(f"   - property_type: {property_data.property_type}")
            
            return property_data
            
        except Exception as e:
            self.logger.error(f"❌ Error processing property data for {raw_data.get('id', 'unknown')}: {e}")
            return None
    
    def _process_basic_info(self, raw_data: Dict) -> Dict:
        """Process basic property information."""
        return {
            'external_id': str(raw_data.get('id', '')),
            'title': raw_data.get('dynamic_title', ''),
            'description': raw_data.get('comment', ''),  # Description is in 'comment' field
            'created_at': self._parse_datetime(raw_data.get('created_at')),
            'updated_at': self._parse_datetime(raw_data.get('last_updated'))
        }
    
    def _process_location(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process location information."""
        property_id = raw_data.get('id', 'unknown')
        
        # Location - use 'address' field from API (not 'street_address')
        raw_address = raw_data.get('address', '')
        
        # More comprehensive address extraction - check different possible fields
        if not raw_address:
            # Try alternative address field names
            raw_address = raw_data.get('street_address', '') or raw_data.get('full_address', '')
        
        # If still no address, try to construct one from street info
        if not raw_address:
            street_name = raw_data.get('street_name', '')
            house_number = raw_data.get('house_number', '') or raw_data.get('building_number', '')
            if street_name:
                raw_address = f"{street_name} {house_number}".strip()
        
        property_data.address = raw_address
        
        # Enhanced logging for address processing
        if raw_address:
            self.logger.info(f"📍 Property {property_id}: Found address '{raw_address}'")
        else:
            self.logger.warning(f"⚠️  Property {property_id}: No address found in raw data")
            # Log all available keys to debug
            address_related_keys = [k for k in raw_data.keys() if any(term in k.lower() for term in ['addr', 'street', 'house', 'building', 'location'])]
            self.logger.warning(f"🔍 Available address-related fields: {address_related_keys}")
            
            # Log the first few keys to see the structure
            all_keys = list(raw_data.keys())[:15]
            self.logger.warning(f"🔍 First 15 raw data keys: {all_keys}")
        
        property_data.city = raw_data.get('city_name') or 'Tbilisi'  # Ensure city is never None
        property_data.state = raw_data.get('district_name') or 'Georgia'  # Ensure state is never None
        property_data.district = raw_data.get('district_name')
        property_data.urban_area = raw_data.get('urban_name')
        
        # Coordinates - use lat/lng from API response
        lat = raw_data.get('lat')
        lng = raw_data.get('lng')
        if lat is not None and lng is not None:
            property_data.latitude = float(lat)
            property_data.longitude = float(lng)
    
    def _process_property_details(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property physical details."""
        property_id = raw_data.get('id', 'unknown')
        
        # Set property type based on real_estate_type_id
        property_type_id = raw_data.get('real_estate_type_id')
        if property_type_id == 1:
            property_data.property_type = 'apartment'
        elif property_type_id == 2:
            property_data.property_type = 'house'
        elif property_type_id == 3:
            property_data.property_type = 'commercial'
        else:
            property_data.property_type = 'apartment'  # Default
        
        # Set listing type based on deal_type_id
        deal_type_id = raw_data.get('deal_type_id')
        self.logger.info(f"🏷️  Processing deal_type_id for property {property_id}: {deal_type_id}")
        
        if deal_type_id == 1:
            property_data.listing_type = 'sale'
            self.logger.info(f"✅ Set listing_type='sale' for property {property_id}")
        elif deal_type_id == 2:
            property_data.listing_type = 'rent'
            self.logger.info(f"✅ Set listing_type='rent' for property {property_id}")
        else:
            property_data.listing_type = 'rent'  # Default since we're focusing on rentals
            self.logger.info(f"🔧 Set default listing_type='rent' for property {property_id} (deal_type_id: {deal_type_id})")
        
        # Convert bedroom and room from strings to integers
        bedroom = raw_data.get('bedroom', '1')
        if isinstance(bedroom, str) and bedroom.isdigit():
            bedroom = int(bedroom)
        elif not isinstance(bedroom, int):
            bedroom = 1
            
        room = raw_data.get('room', '1')
        if isinstance(room, str) and room.isdigit():
            room = int(room)
        elif not isinstance(room, int):
            room = bedroom + 1  # Usually rooms = bedrooms + 1 (living room)
        
        property_data.bedrooms = bedroom
        property_data.bathrooms = self._extract_bathroom_count(raw_data)
        property_data.square_feet = self._safe_int(raw_data.get('area'))  # 'area' field
        property_data.lot_size = self._safe_float(raw_data.get('yard_area'))
    
    def _process_basic_financial(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process basic financial information."""
        # Process main price - could be sale price or rent amount
        price = self._safe_float(raw_data.get('price'))
        if price > 0:
            property_data.rent_amount = price
        
        # Process additional financial fields
        property_data.security_deposit = self._safe_float(raw_data.get('security_deposit'))
        property_data.lease_duration = self._safe_int(raw_data.get('lease_duration'), 12)
    
    def _process_features(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property features."""
        property_id = property_data.external_id
        self.logger.debug(f"🎯 Processing features for property {property_id}")
        
        # Status mapping: 1 = active, 2 = sold/rented, 3 = inactive
        status_id = raw_data.get('status_id', 1)
        self.logger.debug(f"📊 Raw status_id for {property_id}: {status_id}")
        
        # Mark all properties as available for rental listings
        property_data.is_available = True  # Always mark as available since we're scraping active listings
        self.logger.info(f"✅ Setting is_available=True for property {property_id}")
        
        # These fields are not explicitly in the JSON, so set defaults
        property_data.is_furnished = False  # Default - would need to check parameters
        property_data.pets_allowed = False  # Default - would need to check parameters  
        property_data.smoking_allowed = False  # Default - would need to check parameters
        property_data.utilities_included = ''  # Default - would need to check parameters
        
        self.logger.debug(f"🏠 Features set for {property_id}: furnished={property_data.is_furnished}, pets={property_data.pets_allowed}, smoking={property_data.smoking_allowed}")
    
    def _process_building_details(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process building-specific details."""
        property_data.year_built = self._safe_int(raw_data.get('year_built'))
        property_data.parking_spaces = self._safe_int(raw_data.get('parking'), 0)
        property_data.floor_number = self._safe_int(raw_data.get('floor'))
        property_data.total_floors = self._safe_int(raw_data.get('total_floors'))
    
    def _determine_user_type(self, raw_data: Dict) -> str:
        """Determine if listing is from owner or agency."""
        user_type_data = raw_data.get('user_type', {})
        
        if isinstance(user_type_data, dict):
            user_type = user_type_data.get('type', '').lower()
            owner_indicators = ['owner', 'individual', 'private', 'person']
            agency_indicators = ['agency', 'realtor', 'broker', 'company']
            
            if any(indicator in user_type for indicator in owner_indicators):
                return 'owner'
            if any(indicator in user_type for indicator in agency_indicators):
                return 'agency'
        
        agency_fields = ['agency_name', 'company_name', 'broker_name']
        has_agency_info = any(raw_data.get(field) for field in agency_fields)
        
        contact_info = raw_data.get('contact', {})
        has_direct_contact = bool(contact_info.get('phone') or contact_info.get('email'))
        
        if not has_agency_info and has_direct_contact:
            return 'owner'
        
        return 'agency'
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string safely."""
        if not date_str:
            return None
            
        try:
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int."""
        if value is None:
            return default
        try:
            if isinstance(value, str):
                value = value.rstrip('+').strip()
                if not value or not value.replace('.', '').replace('-', '').isdigit():
                    return default
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if value is None:
            return default
        try:
            if isinstance(value, str):
                value = value.rstrip('+').strip()
                if not value or not value.replace('.', '').replace('-', '').isdigit():
                    return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _extract_bathroom_count(self, raw_data: Dict) -> float:
        """Extract bathroom count from parameters or set default."""
        property_id = raw_data.get('id', 'unknown')
        self.logger.debug(f"🚿 Extracting bathroom count for property {property_id}")
        
        try:
            # Check parameters for bathroom-related fields
            parameters = raw_data.get('parameters', [])
            self.logger.debug(f"🔍 Found {len(parameters) if parameters else 0} parameters for {property_id}")
            
            if isinstance(parameters, list):
                for param in parameters:
                    if isinstance(param, dict):
                        key = param.get('key', '').lower()
                        value = param.get('parameter_value', '')
                        
                        # Look for bathroom-related keys
                        if 'bathroom' in key or 'toilet' in key or 'wc' in key:
                            self.logger.info(f"🎯 Found bathroom parameter for {property_id}: {key}={value}")
                            bathroom_count = self._safe_float(value, 1.0)
                            if bathroom_count > 0:
                                self.logger.info(f"✅ Extracted bathroom count for {property_id}: {bathroom_count}")
                                return bathroom_count
            
            # Check direct fields (if any)
            bathroom_field = raw_data.get('bathroom')
            if bathroom_field:
                self.logger.info(f"🎯 Found direct bathroom field for {property_id}: {bathroom_field}")
                return self._safe_float(bathroom_field, 1.0)
            
            # Default based on bedrooms (usually 1 bathroom per bedroom + 1)
            bedrooms = self._safe_int(raw_data.get('bedroom', '1'))
            default_bathrooms = max(1.0, float(bedrooms) * 0.5)  # Reasonable estimate
            self.logger.debug(f"🔧 Using default bathroom count for {property_id}: {default_bathrooms} (based on {bedrooms} bedrooms)")
            return default_bathrooms
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting bathroom count for {property_id}: {e}")
            return 1.0  # Safe default
