"""
Multilingual content processing.
"""
import logging
import aiohttp
from typing import Dict, List, Optional

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


class MultilingualProcessor:
    """Handles multilingual content processing."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the multilingual processor."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Language mappings
        self.language_codes = {
            'ka': 'ka',  # Georgian
            'en': 'en',  # English  
            'ru': 'ru'   # Russian
        }
    
    def is_multilingual_enabled(self) -> bool:
        """Check if multilingual processing is enabled."""
        return self.config.concurrent_languages
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.language_codes.keys())
    
    async def process_multilingual_content(self, session: aiohttp.ClientSession, 
                                         property_data: PropertyData) -> None:
        """Process multilingual content for a property."""
        if not self.is_multilingual_enabled():
            return
        
        try:
            # Get content for each language
            for lang_code in ['en', 'ru']:  # Skip 'ka' as it's already the default
                try:
                    content = await self._fetch_property_in_language(session, property_data.external_id, lang_code)
                    if content:
                        self._update_property_language_content(property_data, content, lang_code)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in multilingual processing for property {property_data.external_id}: {e}")
    
    async def _fetch_property_in_language(self, session: aiohttp.ClientSession,
                                        property_id: str, language: str) -> Optional[Dict]:
        """Fetch property data in a specific language."""
        try:
            # Use the same list endpoint but with different locale
            url = self.config.api_endpoints['list_properties']
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': f'{language}-US,{language};q=0.9,ka;q=0.8,und;q=0.7',
                'global-authorization': '',
                'locale': language,
                'origin': 'https://www.myhome.ge',
                'referer': 'https://www.myhome.ge/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36',
                'x-website-key': 'myhome'
            }
            
            # Search for the specific property in the list
            # We'll search multiple pages to find this property
            default_property_types = getattr(self.config, 'default_property_types', "2,1,3,4,5,6")
            default_deal_types = getattr(self.config, 'default_deal_types', "1,2,3,7")
            per_page = getattr(self.config, 'per_page', 1000)
            
            for page in range(1, 6):  # Check first 5 pages
                params = {
                    'currency_id': 1,  # USD
                    'deal_types': default_deal_types,   # All deal types from config
                    'real_estate_types': default_property_types,  # All property types from config
                    'page': page,
                    'per_page': per_page  # Get maximum properties per request
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('result') and data.get('data') and data['data'].get('data'):
                            properties = data['data']['data']
                            
                            # Look for our property in this page
                            for prop in properties:
                                if str(prop.get('id')) == str(property_id):
                                    return prop
                                    
            return None
            
        except Exception as e:
            return None
    
    def _update_property_language_content(self, property_data: PropertyData, 
                                        content: Dict, language: str) -> None:
        """Update property data with content from specific language."""
        try:
            # Extract title
            title = content.get('dynamic_title') or ''
            title = title.strip() if title else ''
            if title:
                if language == 'en':
                    property_data.title_en = title
                elif language == 'ru':
                    property_data.title_ru = title
                    
            # Extract description (comment field)
            comment = content.get('comment') or ''
            comment = comment.strip() if comment else ''
            if comment:
                if language == 'en':
                    property_data.description_en = comment
                elif language == 'ru':
                    property_data.description_ru = comment
                    
        except Exception as e:
            pass
