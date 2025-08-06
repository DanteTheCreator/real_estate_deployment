"""
Multilingual content processing for standalone worker.
"""
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional

from ..models.property_data import PropertyData
from ..core.config import MultilingualConfig


class MultilingualProcessor:
    """Handles multilingual content processing."""
    
    def __init__(self, config: MultilingualConfig):
        """Initialize the multilingual processor."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Language mappings
        self.language_codes = {
            'ka': 'ka',  # Georgian
            'en': 'en',  # English  
            'ru': 'ru'   # Russian
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.language_codes.keys())
    
    async def process_multilingual_content(self, session: aiohttp.ClientSession, 
                                         property_data: PropertyData) -> None:
        """Process multilingual content for a property."""
        
        try:
            # Try to get content for each language from API
            api_success = False
            
            for lang_code in ['en', 'ru']:  # Skip 'ka' as it's already the default
                try:
                    self.logger.info(f"Fetching property {property_data.external_id} in {lang_code}")
                    content = await self._fetch_property_in_language(session, property_data.external_id, lang_code)
                    self.logger.debug(f"Content returned for {lang_code}: {content is not None}")
                    if content:
                        self._update_property_language_content(property_data, content, lang_code)
                        api_success = True
                        self.logger.info(f"Successfully processed API content for {lang_code}")
                    else:
                        self.logger.warning(f"No content returned for property {property_data.external_id} in {lang_code}")
                        
                    # Small delay between language requests to be respectful
                    await asyncio.sleep(0.5)
                        
                except Exception as e:
                    self.logger.error(f"Failed to fetch property {property_data.external_id} in {lang_code}: {e}")
                    continue
            
            # If API failed completely, use fallback approach with basic translations
            self.logger.debug(f"API success status: {api_success}")
            if not api_success:
                self.logger.info(f"API unavailable, using fallback translation approach for {property_data.external_id}")
                self._apply_fallback_translations(property_data)
            else:
                self.logger.info(f"API content retrieved successfully for {property_data.external_id}")
                    
        except Exception as e:
            self.logger.error(f"Error in multilingual processing for property {property_data.external_id}: {e}")
            # Apply fallback even if everything fails
            self._apply_fallback_translations(property_data)
    
    async def _fetch_property_in_language(self, session: aiohttp.ClientSession,
                                        property_id: str, language: str) -> Optional[Dict]:
        """Fetch property data in a specific language using the correct MyHome.ge API."""
        try:
            # Use the correct MyHome.ge API endpoint structure
            detail_url = f"https://api-statements.tnet.ge/v1/statements/{property_id}"
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': f'{language}-US,{language};q=0.9,ka;q=0.8,und;q=0.7',
                'global-authorization': self.config.API_TOKEN,
                'locale': language,
                'origin': 'https://www.myhome.ge',
                'priority': 'u=1, i',
                'referer': 'https://www.myhome.ge/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'x-website-key': 'myhome'
            }
            
            self.logger.info(f"Fetching property {property_id} in language {language} from {detail_url}")
            
            async with session.get(detail_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Debug: log the response structure
                    self.logger.debug(f"API response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
                    
                    # The detail endpoint should return the property data directly
                    if data.get('result') and data.get('data'):
                        # The actual property data is nested under "statement"
                        if 'statement' in data['data']:
                            property_data = data['data']['statement']
                        else:
                            property_data = data['data']
                            
                        self.logger.info(f"Successfully fetched property {property_id} in {language}")
                        
                        # Debug: log what fields are available
                        if isinstance(property_data, dict):
                            self.logger.debug(f"Property data keys: {list(property_data.keys())[:10]}...")  # First 10 keys
                            title_candidates = [k for k in property_data.keys() if 'title' in k.lower()]
                            desc_candidates = [k for k in property_data.keys() if any(word in k.lower() for word in ['desc', 'comment', 'detail'])]
                            self.logger.debug(f"Title candidates: {title_candidates}")
                            self.logger.debug(f"Description candidates: {desc_candidates}")
                        
                        return property_data
                    else:
                        self.logger.warning(f"No property data found for {property_id} in {language}")
                        return None
                else:
                    self.logger.error(f"Failed to fetch property {property_id} in {language}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching property {property_id} in {language}: {e}")
            return None
    
    def _update_property_language_content(self, property_data: PropertyData, 
                                        content: Dict, language: str) -> None:
        """Update property data with content from specific language."""
        try:
            # Extract title - try multiple possible fields
            title = (content.get('dynamic_title') or 
                    content.get('title') or 
                    content.get('name') or '')
            title = title.strip() if title else ''
            
            if title:
                if language == 'en':
                    property_data.title_en = title
                    self.logger.info(f"Set English title: {title[:50]}...")
                elif language == 'ru':
                    property_data.title_ru = title
                    self.logger.info(f"Set Russian title: {title[:50]}...")
                    
            # Extract description - try multiple possible fields
            description = (content.get('comment') or 
                          content.get('description') or 
                          content.get('details') or '')
            description = description.strip() if description else ''
            
            if description:
                if language == 'en':
                    property_data.description_en = description
                    self.logger.info(f"Set English description: {description[:100]}...")
                elif language == 'ru':
                    property_data.description_ru = description
                    self.logger.info(f"Set Russian description: {description[:100]}...")
            else:
                self.logger.warning(f"No description found for property {property_data.external_id} in {language}")
                    
        except Exception as e:
            self.logger.error(f"Error updating property content for {language}: {e}")
            pass

    def _apply_fallback_translations(self, property_data: PropertyData) -> None:
        """Apply basic fallback translations when API is unavailable."""
        try:
            # Basic Georgian to English/Russian transliterations and common translations
            georgian_title = property_data.title or ""
            georgian_desc = property_data.description or ""
            
            # Simple translation patterns for common Georgian real estate terms
            translation_map = {
                'ka': {
                    'იყიდება': {'en': 'For Sale', 'ru': 'Продается'},
                    'ქირავდება': {'en': 'For Rent', 'ru': 'Сдается в аренду'},
                    'ბინა': {'en': 'Apartment', 'ru': 'Квартира'},
                    'სახლი': {'en': 'House', 'ru': 'Дом'},
                    'ოთახი': {'en': 'Room', 'ru': 'Комната'},
                    'ოთახიანი': {'en': 'Room', 'ru': 'комнатный'},
                    'კომერციული': {'en': 'Commercial', 'ru': 'Коммерческий'},
                    'ოფისი': {'en': 'Office', 'ru': 'Офис'},
                    'მაღაზია': {'en': 'Shop', 'ru': 'Магазин'},
                    'ავტოფარეხი': {'en': 'Garage', 'ru': 'Гараж'},
                    'ზღვის': {'en': 'Sea', 'ru': 'Море'},
                    'ცენტრი': {'en': 'Center', 'ru': 'Центр'},
                    'ახალი': {'en': 'New', 'ru': 'Новый'},
                    'რემონტი': {'en': 'Renovation', 'ru': 'Ремонт'},
                    'ავეჯი': {'en': 'Furniture', 'ru': 'Мебель'},
                    'ლიფტი': {'en': 'Elevator', 'ru': 'Лифт'},
                    'ბალკონი': {'en': 'Balcony', 'ru': 'Балкон'},
                    'ტელეფონი': {'en': 'Phone', 'ru': 'Телефон'},
                    'ინტერნეტი': {'en': 'Internet', 'ru': 'Интернет'}
                }
            }
            
            # Apply basic translations to title
            en_title = georgian_title
            ru_title = georgian_title
            
            for ka_term, translations in translation_map['ka'].items():
                if ka_term in georgian_title:
                    en_title = en_title.replace(ka_term, translations['en'])
                    ru_title = ru_title.replace(ka_term, translations['ru'])
            
            # Apply basic translations to description
            en_desc = georgian_desc
            ru_desc = georgian_desc
            
            for ka_term, translations in translation_map['ka'].items():
                if ka_term in georgian_desc:
                    en_desc = en_desc.replace(ka_term, translations['en'])
                    ru_desc = ru_desc.replace(ka_term, translations['ru'])
            
            # Set the translated content if we made changes
            if en_title != georgian_title:
                property_data.title_en = en_title.strip()
                self.logger.info(f"Applied fallback English title: {en_title[:50]}...")
            
            if ru_title != georgian_title:
                property_data.title_ru = ru_title.strip()
                self.logger.info(f"Applied fallback Russian title: {ru_title[:50]}...")
            
            if en_desc != georgian_desc and georgian_desc:
                property_data.description_en = en_desc.strip()
                self.logger.info(f"Applied fallback English description")
            
            if ru_desc != georgian_desc and georgian_desc:
                property_data.description_ru = ru_desc.strip()
                self.logger.info(f"Applied fallback Russian description")
                
        except Exception as e:
            self.logger.error(f"Error applying fallback translations: {e}")
