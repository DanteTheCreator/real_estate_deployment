from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import sys
import os
import requests
import logging
import json
import time
from urllib.parse import urljoin
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

sys.path.append('/root/real_estate_deployment/back-end')

# Import the correct schemas and models
from schemas import PropertyCreate, PropertyImageCreate, AmenityCreate, PropertyType, ListingType, UserRole
from database import Property, PropertyImage, PropertyParameter, PropertyPrice, Parameter, User, get_db, SessionLocal, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyHomeEnhancedScraper:
    def __init__(self, base_url: str = "https://api-statements.tnet.ge/v1/statements"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set up headers to exactly match the working curl request
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,ka;q=0.8,und;q=0.7',
            'global-authorization': '',
            'locale': 'ka',
            'origin': 'https://www.myhome.ge',
            'priority': 'u=1, i',
            'referer': 'https://www.myhome.ge/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-website-key': 'myhome'
        })
        
        # Property type mappings from Georgian API to your schema
        self.property_type_mapping = {
            1: "apartment",  # Apartment
            2: "house",      # House
            3: "condo",      # Commercial
            4: "townhouse",  # Villa/Townhouse
            5: "studio"      # Studio
        }
        
        # Deal type mappings
        self.deal_type_mapping = {
            1: "sale",
            2: "rent", 
            3: "lease",
            7: "daily"
        }
        
        # Currency mappings
        self.currency_mapping = {
            1: "USD",
            2: "GEL",  # Georgian Lari
            3: "EUR"
        }

    def fetch_properties_data(self, limit: int = 50, page: int = 1) -> Optional[Dict]:
        """
        Fetch properties data from MyHome.ge API (v1/statements)
        """
        try:
            url = self.base_url
            params = {
                'currency_id': 1,  # USD
                # Remove deal_types restriction to fetch all listing types (sale, rent, lease, daily)
                'page': page
            }
            # Only add limit if it's different from default API behavior
            if limit != 50:  # API default seems to be around 50
                params['limit'] = limit
                
            logger.info(f"Making API request to {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # The API returns: {"result": true, "data": {"data": [properties]}}
            if data.get('result') and data.get('data') and data['data'].get('data'):
                properties = data['data']['data']
                logger.info(f"Successfully fetched {len(properties)} properties")
                # Debug: Check the structure of the first property
                if properties and len(properties) > 0:
                    first_property = properties[0]
                    logger.info(f"First property type: {type(first_property)}")
                    if isinstance(first_property, dict):
                        logger.info(f"First property keys: {list(first_property.keys())[:10]}")
                        logger.info(f"First property ID: {first_property.get('id', 'NO_ID')}")
                    else:
                        logger.warning(f"First property is not a dict: {str(first_property)[:200]}")
                # Return the structure expected by the rest of the code
                return {'result': True, 'data': properties}
            else:
                logger.warning("No data returned from API")
                logger.warning(f"API response: {data}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return None

    def create_default_user(self, db: Session) -> User:
        """Create a default system user for scraped properties"""
        default_user = db.query(User).filter(User.email == "system@scraper.com").first()
        
        if not default_user:
            default_user = User(
                email="system@scraper.com",
                first_name="System",
                last_name="Scraper",
                password_hash="dummy_hash",  # This won't be used for login
                role="admin",
                is_active=True,
                is_verified=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            logger.info("Created default system user")
        
        return default_user

    def create_or_get_parameters(self, db: Session, parameters_data: List[Dict]) -> List[Parameter]:
        """Create or get parameters from the external API data"""
        created_parameters = []
        
        for param_data in parameters_data:
            external_id = param_data.get('id')
            if not external_id:
                continue
                
            # Check if parameter already exists
            existing_param = db.query(Parameter).filter(Parameter.external_id == external_id).first()
            
            if not existing_param:
                # Create new parameter
                parameter = Parameter(
                    external_id=external_id,
                    key=param_data.get('key', ''),
                    sort_index=param_data.get('sort_index', 0),
                    deal_type_id=param_data.get('deal_type_id'),
                    input_name=param_data.get('input_name'),
                    select_name=param_data.get('select_name'),
                    svg_file_name=param_data.get('svg_file_name'),
                    background_color=param_data.get('background_color'),
                    parameter_type=param_data.get('parameter_type', 'parameter'),
                    display_name=param_data.get('display_name', param_data.get('key', ''))
                )
                db.add(parameter)
                created_parameters.append(parameter)
            else:
                created_parameters.append(existing_param)
        
        if created_parameters:
            db.commit()
            
        return created_parameters

    def find_existing_property(self, db: Session, property_data: Dict, external_id: int) -> Optional[Property]:
        """
        Enhanced deduplication logic to find existing properties
        Checks multiple criteria to prevent duplicates
        """
        # Primary check: external_id + source (most reliable)
        existing = db.query(Property).filter(
            Property.external_id == str(external_id),
            Property.source == 'myhome.ge'
        ).first()
        
        if existing:
            return existing
        
        # Secondary check: coordinates + basic details (for properties that might have different external IDs)
        lat = property_data.get('lat')
        lng = property_data.get('lng')
        address = property_data.get('address', '').strip()
        
        if lat and lng:
            # Check for properties with same coordinates and similar details
            coordinate_match = db.query(Property).filter(
                and_(
                    Property.latitude.isnot(None),
                    Property.longitude.isnot(None),
                    func.abs(Property.latitude - lat) < 0.0001,  # Very close coordinates
                    func.abs(Property.longitude - lng) < 0.0001,
                    Property.source == 'myhome.ge'
                )
            ).first()
            
            if coordinate_match:
                logger.info(f"Found potential coordinate duplicate for property {external_id}")
                return coordinate_match
        
        # Tertiary check: address + rent amount (for properties with same address)
        if address:
            price_data = property_data.get('price', {})
            rent_amount = 0.0
            if price_data:
                if '1' in price_data and price_data['1'].get('price_total'):
                    rent_amount = float(price_data['1']['price_total'])  # USD
                elif '2' in price_data and price_data['2'].get('price_total'):
                    rent_amount = float(price_data['2']['price_total'])  # GEL
            
            if rent_amount > 0:
                address_match = db.query(Property).filter(
                    and_(
                        Property.address.ilike(f"%{address}%"),
                        func.abs(Property.rent_amount - rent_amount) < 50,  # Within $50
                        Property.source == 'myhome.ge'
                    )
                ).first()
                
                if address_match:
                    logger.info(f"Found potential address duplicate for property {external_id}")
                    return address_match
        
        return None

    def cleanup_old_properties(self, db: Session, days_old: int = 30) -> int:
        """
        Remove properties that haven't been updated in specified days
        This helps remove properties that are no longer available
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Find old properties from this source
            old_properties = db.query(Property).filter(
                and_(
                    Property.source == 'myhome.ge',
                    Property.last_scraped < cutoff_date
                )
            ).all()
            
            count = len(old_properties)
            if count > 0:
                # Delete old properties
                for prop in old_properties:
                    db.delete(prop)
                db.commit()
                logger.info(f"Cleaned up {count} old properties (older than {days_old} days)")
            
            return count
        except Exception as e:
            logger.error(f"Error cleaning up old properties: {e}")
            db.rollback()
            return 0

    def save_property_to_db(self, db: Session, property_data: Dict, default_user: User) -> Optional[Property]:
        """Save a single property to database using your actual models"""
        try:
            # Debug: Print the type and structure of property_data
            logger.info(f"Property data type: {type(property_data)}")
            if isinstance(property_data, str):
                logger.error(f"Property data is a string instead of dict: {property_data[:200]}...")
                return None
            
            if not isinstance(property_data, dict):
                logger.error(f"Property data is not a dictionary: {type(property_data)}")
                return None
                
            external_id = property_data.get('id')
            if not external_id:
                logger.error("No external ID found for property")
                logger.debug(f"Property data keys: {list(property_data.keys())}")
                return None
            
            # Enhanced deduplication check
            existing_property = self.find_existing_property(db, property_data, external_id)
            
            # Prepare property data mapping from my-home.ge API to traditional rental schema
            price_data = property_data.get('price', {})
            
            # Map property type from external ID to string
            property_type_id = property_data.get('real_estate_type_id', 1)
            property_type = self.property_type_mapping.get(property_type_id, "apartment")
            
            # Map deal type from external ID to string
            deal_type_id = property_data.get('deal_type_id', 2)
            listing_type = self.deal_type_mapping.get(deal_type_id, "rent")
            
            # Get rent amount from price data (prefer USD, fallback to GEL)
            rent_amount = 0.0
            rent_amount_usd = None
            
            if price_data:
                # Price data structure: {"1": {"price_total": 1220, "price_square": 24}, "2": {...}}
                # Currency mapping: 1=USD, 2=GEL, 3=EUR
                
                # Always capture USD amount if available
                if '1' in price_data and price_data['1'].get('price_total'):
                    rent_amount_usd = float(price_data['1']['price_total'])
                    rent_amount = rent_amount_usd  # Primary rent amount in USD
                
                # If no USD, use GEL as primary but don't set USD
                if rent_amount == 0.0 and '2' in price_data and price_data['2'].get('price_total'):
                    rent_amount = float(price_data['2']['price_total'])  # GEL
                
                # If neither USD nor GEL, use EUR as last resort
                if rent_amount == 0.0 and '3' in price_data and price_data['3'].get('price_total'):
                    rent_amount = float(price_data['3']['price_total'])  # EUR
            
            # Helper function to safely convert to int
            def safe_int(value, default=0):
                if value is None:
                    return default
                try:
                    # Handle string values like "10+"
                    if isinstance(value, str):
                        # Remove + signs and other non-numeric characters
                        value = value.rstrip('+').strip()
                        if not value or not value.replace('.', '').isdigit():
                            return default
                    return int(float(value))
                except (ValueError, TypeError):
                    return default
                    
            # Helper function to safely convert to float
            def safe_float(value, default=0.0):
                if value is None:
                    return default
                try:
                    # Handle string values like "10+"
                    if isinstance(value, str):
                        # Remove + signs and other non-numeric characters
                        value = value.rstrip('+').strip()
                        if not value or not value.replace('.', '').isdigit():
                            return default
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            # Prepare property data matching traditional rental schema
            property_kwargs = {
                # Basic info matching traditional schema
                'title': property_data.get('dynamic_title') or property_data.get('title') or f'Property {external_id}',
                'description': property_data.get('comment', ''),
                'address': property_data.get('address', ''),
                'city': property_data.get('city_name', 'Tbilisi'),
                'state': property_data.get('district_name', 'Georgia'),
                'zip_code': '0000',  # MyHome.ge doesn't provide zip codes
                'country': 'Georgia',
                'property_type': property_type,
                'listing_type': listing_type,
                'bedrooms': safe_int(property_data.get('bedroom')),
                'bathrooms': safe_float(property_data.get('room'), 1.0),  # Approximate bathrooms from rooms
                'square_feet': safe_int(property_data.get('area')),
                'lot_size': safe_float(property_data.get('yard_area')),
                'rent_amount': rent_amount,
                'rent_amount_usd': rent_amount_usd,
                'security_deposit': None,  # Not provided by API
                'lease_duration': 12,  # Default to 12 months
                'available_date': None,
                'is_available': True,  # Mark all scraped listings as available
                'is_furnished': False,  # Would need to check parameters for this
                'pets_allowed': False,  # Would need to check parameters for this
                'smoking_allowed': False,  # Would need to check parameters for this
                'year_built': None,
                'parking_spaces': 0,  # Would need to check parameters for this
                'utilities_included': None,
                'district': property_data.get('district_name'),
                'urban_area': property_data.get('urban_name'),
                'latitude': property_data.get('lat'),
                'longitude': property_data.get('lng'),
                'floor_number': safe_int(property_data.get('floor')),
                'total_floors': safe_int(property_data.get('total_floors')),
                'external_id': str(external_id),
                'source': 'myhome.ge',
                'user_type': property_data.get('user_type', {}).get('type') if property_data.get('user_type') else None,
                'last_scraped': datetime.now(),
                'owner_id': default_user.id,
            }
            
            if existing_property:
                # Update existing property
                for key, value in property_kwargs.items():
                    setattr(existing_property, key, value)
                
                db.commit()
                db.refresh(existing_property)
                property_obj = existing_property
                logger.info(f"Updated existing property: {external_id}")
            else:
                # Create new property
                property_obj = Property(**property_kwargs)
                db.add(property_obj)
                db.commit()
                db.refresh(property_obj)
                logger.info(f"Created new property: {external_id}")
            
            # Handle parameters
            parameters_data = property_data.get('parameters', [])
            if parameters_data:
                # Remove existing property parameters for updates
                if existing_property:
                    db.query(PropertyParameter).filter(PropertyParameter.property_id == property_obj.id).delete()
                
                # Create or get parameters
                parameters = self.create_or_get_parameters(db, parameters_data)
                
                # Create property parameter relationships
                for param_data, parameter in zip(parameters_data, parameters):
                    property_param = PropertyParameter(
                        property_id=property_obj.id,
                        parameter_id=parameter.id,
                        parameter_value=param_data.get('parameter_value'),
                        parameter_select_name=param_data.get('parameter_select_name')
                    )
                    db.add(property_param)
                
                db.commit()
            
            # Handle prices
            price_data = property_data.get('price', {})
            if price_data:
                # Remove existing prices for updates
                if existing_property:
                    db.query(PropertyPrice).filter(PropertyPrice.property_id == property_obj.id).delete()
                
                # Create new price records
                for currency_type, price_info in price_data.items():
                    if isinstance(price_info, dict) and price_info.get('price_total'):
                        property_price = PropertyPrice(
                            property_id=property_obj.id,
                            currency_type=currency_type,
                            price_total=float(price_info.get('price_total', 0)),
                            price_square=float(price_info.get('price_square', 0))
                        )
                        db.add(property_price)
                
                db.commit()
            
            # Handle images
            images_data = property_data.get('images', [])
            if images_data:
                # Remove existing images for updates
                if existing_property:
                    db.query(PropertyImage).filter(PropertyImage.property_id == property_obj.id).delete()
                
                # Create new image records
                for idx, image_data in enumerate(images_data):
                    # Use the large image URL as the primary URL
                    image_url = image_data.get('large', image_data.get('thumb', ''))
                    if image_url:
                        property_image = PropertyImage(
                            property_id=property_obj.id,
                            image_url=image_url,
                            caption=None,  # MyHome.ge doesn't provide captions
                            is_primary=image_data.get('is_main', False) or idx == 0,  # First image is primary if none marked
                            order_index=idx
                        )
                        db.add(property_image)
                
                db.commit()
            
            return property_obj
                
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error saving property: {e}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving property to database: {e}")
            return None

    def scrape_and_save(self, max_properties: int = 500000, batch_size: int = 50) -> Dict[str, int]:
        """Main method to scrape properties and save to database"""
        stats = {
            'total_fetched': 0,
            'new_properties': 0,
            'updated_properties': 0,
            'duplicates_skipped': 0,
            'cleaned_old': 0,
            'errors': 0
        }
        
        db = SessionLocal()
        try:
            default_user = self.create_default_user(db)
            
            # First, cleanup old properties (run cleanup every time)
            cleanup_days = int(os.getenv('CLEANUP_DAYS', 30))
            stats['cleaned_old'] = self.cleanup_old_properties(db, cleanup_days)
            
            properties_processed = 0
            page = 1
            
            while properties_processed < max_properties:
                current_batch_size = min(batch_size, max_properties - properties_processed)
                data = self.fetch_properties_data(limit=current_batch_size, page=page)
                
                if not data or not data.get('data'):
                    logger.info("No more properties to fetch")
                    break
                
                properties = data['data']
                stats['total_fetched'] += len(properties)
                
                # Debug: Check what we actually got
                logger.info(f"Properties data type: {type(properties)}")
                if properties:
                    logger.info(f"First property type: {type(properties[0])}")
                    if isinstance(properties[0], dict):
                        logger.info(f"First property ID: {properties[0].get('id', 'NO_ID')}")
                    else:
                        logger.warning(f"First property value: {properties[0]}")
                
                # Process each property
                for idx, property_data in enumerate(properties):
                    try:
                        logger.info(f"Processing property {idx + 1}/{len(properties)}")
                        saved_property = self.save_property_to_db(db, property_data, default_user)
                        
                        if saved_property:
                            # Check if it was an update or new creation
                            if saved_property.created_at.date() == datetime.now().date():
                                stats['new_properties'] += 1
                            else:
                                stats['updated_properties'] += 1
                        else:
                            stats['errors'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing property: {e}")
                        stats['errors'] += 1
                        continue
                
                properties_processed += len(properties)
                page += 1
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)  # Reduced from 1 second to 0.1 seconds
                
                logger.info(f"Processed {properties_processed}/{max_properties} properties")
                
                # Break only if we got no properties at all (end of data)
                if len(properties) == 0:
                    logger.info("No properties returned, reached end of data")
                    break
        
        except Exception as e:
            logger.error(f"Error in main scraping process: {e}")
            stats['errors'] += 1
        
        finally:
            db.close()
        
        return stats

def main():
    """Main function to run the scraper"""
    scraper = MyHomeEnhancedScraper()
    
    # Configuration
    MAX_PROPERTIES = int(os.getenv('MAX_PROPERTIES', 100))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 20))
    
    logger.info(f"Starting enhanced scraper - Max properties: {MAX_PROPERTIES}, Batch size: {BATCH_SIZE}")
    
    # Run scraper
    stats = scraper.scrape_and_save(max_properties=MAX_PROPERTIES, batch_size=BATCH_SIZE)
    
    # Print results
    logger.info("=== Scraping Results ===")
    logger.info(f"Total fetched: {stats['total_fetched']}")
    logger.info(f"New properties: {stats['new_properties']}")
    logger.info(f"Updated properties: {stats['updated_properties']}")
    logger.info(f"Duplicates skipped: {stats.get('duplicates_skipped', 0)}")
    logger.info(f"Old properties cleaned: {stats.get('cleaned_old', 0)}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info("=== Scraping Complete ===")
    
    return stats

if __name__ == "__main__":
    main()