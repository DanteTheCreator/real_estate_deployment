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
        """Convert raw property data to PropertyData object - SPEED OPTIMIZED."""
        try:
            # Create PropertyData instance with basic info
            basic_info = self._process_basic_info(raw_data)
            property_data = PropertyData(**basic_info)
            
            # Process different aspects of the property
            self._process_location(property_data, raw_data)
            self._process_property_details(property_data, raw_data)
            self._process_basic_financial(raw_data, property_data)
            self._process_features(property_data, raw_data)
            self._process_building_details(property_data, raw_data)
            self._process_photos(property_data, raw_data)
            
            # Set user type (owner vs agency)
            property_data.user_type = self._determine_user_type(raw_data)
            
            return property_data
            
        except Exception as e:
            self.logger.error(f"Error processing property {raw_data.get('id', 'unknown')}: {e}")
            return None
    
    def _process_basic_info(self, raw_data: Dict) -> Dict:
        """Process basic property information."""
        title = raw_data.get('dynamic_title', '')
        if not title:  # Fallback to other title fields
            title = raw_data.get('title', '') or raw_data.get('dynamic_slug', '') or f"Property {raw_data.get('id', 'Unknown')}"
        
        result = {
            'external_id': str(raw_data.get('id', '')),
            'title': title,
            'description': raw_data.get('comment', ''),  # Description is in 'comment' field
            'created_at': self._parse_datetime(raw_data.get('created_at')),
            'updated_at': self._parse_datetime(raw_data.get('last_updated')),
            'source': 'myhome.ge'
        }
        
        return result
    
    def _process_location(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process location information - SPEED OPTIMIZED."""
        # Location - use 'address' field from API
        raw_address = raw_data.get('address', '')
        
        # Try alternative address field names if needed
        if not raw_address:
            raw_address = raw_data.get('street_address', '') or raw_data.get('full_address', '')
        
        # Construct from street info if still empty
        if not raw_address:
            street_name = raw_data.get('street_name', '')
            house_number = raw_data.get('house_number', '') or raw_data.get('building_number', '')
            if street_name:
                raw_address = f"{street_name} {house_number}".strip()
        
        property_data.address = raw_address
        property_data.city = raw_data.get('city_name') or 'Tbilisi'
        property_data.state = raw_data.get('district_name') or 'Georgia'
        property_data.district = raw_data.get('district_name')
        property_data.urban_area = raw_data.get('urban_name')
        
        # Add metro station information to utilities_included if available
        metro_station = raw_data.get('metro_station')
        if metro_station:
            if property_data.utilities_included:
                property_data.utilities_included += f", Metro: {metro_station}"
            else:
                property_data.utilities_included = f"Metro: {metro_station}"
        
        # Coordinates
        lat = raw_data.get('lat')
        lng = raw_data.get('lng')
        if lat is not None and lng is not None:
            property_data.latitude = float(lat)
            property_data.longitude = float(lng)
    
    def _process_property_details(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property physical details - SPEED OPTIMIZED."""
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
        if deal_type_id == 1:
            property_data.listing_type = 'sale'
        elif deal_type_id == 2:
            property_data.listing_type = 'rent'
        else:
            property_data.listing_type = 'rent'  # Default
        
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
        property_data.square_feet = self._safe_int(raw_data.get('area'))
        property_data.lot_size = self._safe_float(raw_data.get('yard_area'))
        
        # Store total rooms count if needed (could be used in utilities_included or other field)
        if room != bedroom:
            # Store room count information in description or utilities_included if different
            property_data.utilities_included = f"Total rooms: {room}"
    
    def _process_basic_financial(self, raw_data: Dict, property_data: PropertyData) -> None:
        """Process basic financial information."""
        # Handle price structure from API response
        price_data = raw_data.get('price', {})
        # FROM EXAMPLE: "1": 1081 (high=GEL), "2": 400 (low=USD), "3": 346 (lowest=EUR)
        currency_map = {1: 'GEL', 2: 'USD', 3: 'EUR'}  # FINAL CORRECT MAPPING
        
        # Extract price from the price structure
        if isinstance(price_data, dict):
            # Currency 1 = GEL (higher values like 1081)
            gel_price_info = price_data.get('1')
            # Currency 2 = USD (lower values like 400)
            usd_price_info = price_data.get('2')
            
            # Set GEL amount (primary currency - higher values)
            if gel_price_info and isinstance(gel_price_info, dict):
                gel_price_total = gel_price_info.get('price_total', 0)
                if gel_price_total and gel_price_total > 0:
                    property_data.rent_amount = gel_price_total
            
            # Set USD amount (secondary currency - lower values)
            if usd_price_info and isinstance(usd_price_info, dict):
                usd_price_total = usd_price_info.get('price_total', 0)
                if usd_price_total and usd_price_total > 0:
                    property_data.rent_amount_usd = usd_price_total
            
            # Fallback: if no GEL price but have other currencies, use the first available
            if property_data.rent_amount == 0.0 and price_data:
                fallback_price_info = next(iter(price_data.values()))
                if fallback_price_info and isinstance(fallback_price_info, dict):
                    fallback_price_total = fallback_price_info.get('price_total', 0)
                    if fallback_price_total and fallback_price_total > 0:
                        property_data.rent_amount = fallback_price_total
        
        # Process all price currencies for the prices list
        self._process_all_prices(raw_data, property_data)
    
    def _process_all_prices(self, raw_data: Dict, property_data: PropertyData) -> None:
        """Process all price currencies to populate the prices list."""
        price_data = raw_data.get('price', {})
        if not isinstance(price_data, dict):
            return
        
        # Process each currency in the price data
        for currency_id, price_info in price_data.items():
            if isinstance(price_info, dict):
                price_total = price_info.get('price_total', 0)
                price_square = price_info.get('price_square', 0)
                
                if price_total and price_total > 0:
                    # Create PropertyPrice object using direct instantiation
                    property_price = type('PropertyPrice', (), {
                        'currency_type': str(currency_id),
                        'price_total': float(price_total),
                        'price_square': float(price_square) if price_square else 0.0,
                        'to_dict': lambda self: {
                            'currency_type': self.currency_type,
                            'price_total': self.price_total,
                            'price_square': self.price_square
                        }
                    })()
                    property_data.prices.append(property_price)
    
    def _process_features(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property features - SPEED OPTIMIZED."""
        # Mark all properties as available since we're scraping active listings
        property_data.is_available = True
        
        # Analyze parameters to determine features
        parameters = raw_data.get('parameters', [])
        furnished_indicators = ['furniture', 'furnished', 'appliance']
        pet_indicators = ['pet', 'animal']
        
        property_data.is_furnished = False
        property_data.pets_allowed = False
        
        if isinstance(parameters, list):
            for param in parameters:
                if isinstance(param, dict):
                    key = param.get('key', '').lower()
                    display_name = param.get('display_name', '').lower()
                    
                    # Check for furnished indicators
                    if any(indicator in key or indicator in display_name for indicator in furnished_indicators):
                        property_data.is_furnished = True
                    
                    # Check for pet indicators
                    if any(indicator in key or indicator in display_name for indicator in pet_indicators):
                        property_data.pets_allowed = True
        
        # Set defaults for other features
        property_data.smoking_allowed = False  # Most rentals don't allow smoking
        
        # Process parameters from API response
        self._process_parameters(property_data, raw_data)
    
    def _process_building_details(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process building-specific details."""
        property_data.year_built = self._safe_int(raw_data.get('year_built'))
        property_data.parking_spaces = self._safe_int(raw_data.get('parking'), 0)
        property_data.floor_number = self._safe_int(raw_data.get('floor'))
        property_data.total_floors = self._safe_int(raw_data.get('total_floors'))
        
        # Store additional information in utilities_included
        additional_info = []
        
        # VIP status information
        if raw_data.get('is_vip'):
            additional_info.append("VIP listing")
        if raw_data.get('is_super_vip'):
            additional_info.append("Super VIP listing")
        
        # Property features
        if raw_data.get('has_3d'):
            additional_info.append("3D tour available")
        
        # Price negotiability
        if raw_data.get('price_negotiable'):
            additional_info.append("Price negotiable")
        if raw_data.get('price_from'):
            additional_info.append("Price from")
        
        # Days on market
        quantity_of_day = raw_data.get('quantity_of_day')
        if quantity_of_day:
            additional_info.append(f"Listed {quantity_of_day} days ago")
        
        # Add to utilities_included if we have additional info
        if additional_info:
            additional_info_str = "; ".join(additional_info)
            if property_data.utilities_included:
                property_data.utilities_included += f"; {additional_info_str}"
            else:
                property_data.utilities_included = additional_info_str
    
    def _determine_user_type(self, raw_data: Dict) -> str:
        """Determine if listing is from owner or agency."""
        # Check user_type field first
        user_type_data = raw_data.get('user_type', {})
        
        if isinstance(user_type_data, dict):
            user_type = user_type_data.get('type', '').lower()
            owner_indicators = ['owner', 'individual', 'private', 'person']
            agency_indicators = ['agency', 'realtor', 'broker', 'company']
            
            if any(indicator in user_type for indicator in owner_indicators):
                return 'owner'
            if any(indicator in user_type for indicator in agency_indicators):
                return 'agency'
        
        # Check for agency-specific fields
        user_title = raw_data.get('user_title', '')
        agency_fields = ['agency_name', 'company_name', 'broker_name']
        has_agency_info = any(raw_data.get(field) for field in agency_fields)
        
        # If user_title contains agency-related terms
        agency_terms = ['agency', 'realtor', 'broker', 'company', 'estate']
        if user_title and any(term in user_title.lower() for term in agency_terms):
            return 'agency'
        
        contact_info = raw_data.get('contact', {})
        has_direct_contact = bool(contact_info.get('phone') or contact_info.get('email'))
        
        # Default logic: if no agency info and has direct contact, likely owner
        if not has_agency_info and has_direct_contact:
            return 'owner'
        
        # Check if user has many listings (agencies typically have more listings)
        user_statements_count = raw_data.get('user_statements_count', 0)
        if user_statements_count > 5:  # Agencies typically have many listings
            return 'agency'
        
        return 'agency'  # Default to agency to be safe
    
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
        """Extract bathroom count - SPEED OPTIMIZED."""
        try:
            # Check parameters for bathroom-related fields
            parameters = raw_data.get('parameters', [])
            
            if isinstance(parameters, list):
                for param in parameters:
                    if isinstance(param, dict):
                        key = param.get('key', '').lower()
                        value = param.get('parameter_value', '')
                        
                        # Look for bathroom-related keys
                        if 'bathroom' in key or 'toilet' in key or 'wc' in key:
                            bathroom_count = self._safe_float(value, 1.0)
                            if bathroom_count > 0:
                                return bathroom_count
            
            # Check direct fields
            bathroom_field = raw_data.get('bathroom')
            if bathroom_field:
                return self._safe_float(bathroom_field, 1.0)
            
            # Default based on bedrooms
            bedrooms = self._safe_int(raw_data.get('bedroom', '1'))
            return max(1.0, float(bedrooms) * 0.5)
            
        except Exception:
            return 1.0  # Safe default

    def _process_photos(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property photos from API response."""
        images = raw_data.get('images', [])
        if not images or not isinstance(images, list):
            return
        
        # Process each image from the API response
        for idx, image in enumerate(images):
            if isinstance(image, dict):
                # Get the large image URL (highest quality)
                large_url = image.get('large')
                if large_url:
                    # Clean up the URL (remove escape characters)
                    clean_url = large_url.replace('\\/', '/')
                    
                    # Check if this is the main photo
                    is_main = image.get('is_main', False)
                    
                    # Create PropertyImage object using direct instantiation
                    property_image = type('PropertyImage', (), {
                        'url': clean_url,
                        'caption': None,
                        'is_primary': is_main,
                        'order_index': idx,
                        'blur_url': image.get('blur', '').replace('\\/', '/') if image.get('blur') else None,
                        'thumbnail_url': image.get('thumb', '').replace('\\/', '/') if image.get('thumb') else None,
                        'to_dict': lambda self: {
                            'image_url': self.url,
                            'caption': self.caption,
                            'is_primary': self.is_primary,
                            'order_index': self.order_index
                        }
                    })()
                    property_data.images.append(property_image)
    
    def _process_parameters(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property parameters from API response."""
        parameters = raw_data.get('parameters', [])
        if not parameters or not isinstance(parameters, list):
            return
            
        # Store the full parameter data for later database parameter creation
        property_data.raw_parameters = parameters
        
        # Process each parameter from the API response
        for param in parameters:
            if isinstance(param, dict):
                param_id = param.get('id')
                if param_id:
                    # Create PropertyParameter object for database storage
                    # Use direct class instantiation instead of imports
                    property_parameter = type('PropertyParameter', (), {
                        'parameter_id': param_id,
                        'parameter_value': param.get('parameter_value'),
                        'parameter_select_name': param.get('parameter_select_name'),
                        'to_dict': lambda self: {
                            'parameter_id': self.parameter_id,
                            'parameter_value': self.parameter_value,
                            'parameter_select_name': self.parameter_select_name
                        }
                    })()
                    property_data.parameters.append(property_parameter)
