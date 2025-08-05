"""
Multilingual content processing.
"""
import logging
import asyncio
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
                    self.logger.info(f"Fetching property {property_data.external_id} in {lang_code}")
                    content = await self._fetch_property_in_language(session, property_data.external_id, lang_code)
                    if content:
                        self._update_property_language_content(property_data, content, lang_code)
                    else:
                        self.logger.warning(f"No content returned for property {property_data.external_id} in {lang_code}")
                        
                    # Small delay between language requests to be respectful
                    await asyncio.sleep(0.5)
                        
                except Exception as e:
                    self.logger.error(f"Failed to fetch property {property_data.external_id} in {lang_code}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in multilingual processing for property {property_data.external_id}: {e}")
    
    async def _fetch_property_in_language(self, session: aiohttp.ClientSession,
                                        property_id: str, language: str) -> Optional[Dict]:
        """Fetch property data in a specific language using the detail endpoint."""
        try:
            # Use the property detail endpoint directly
            base_url = self.config.api_endpoints['list_properties']  # Get base API URL
            detail_url = f"{base_url}/{property_id}"
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': f'{language}-US,{language};q=0.9,ka;q=0.8,und;q=0.7',
                'global-authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ2IjoxLCJpYXQiOjE3NTQzODU3NjksImV4cGlyZXNfYXQiOjE3NTQzODY0MjksImRhdGEiOnsidXNlcl9pZCI6NTEwNTQzMywidXNlcm5hbWUiOiJrYXhhbWlxZWxhZHplQGdtYWlsLmNvbSIsInNlc3Npb25faWQiOiIzYzA2NjE4YjU0NGMyMTI4MTBkN2NhYjRhMDQ1Mzk5MDFlYThmZDljNWEwN2FhMWE3ZmI4NTdhMTdlOWVjNGZiIiwibGl2b191c2VyX2lkIjpudWxsLCJzd29vcF91c2VyX2lkIjozODQxNjAsInRrdF91c2VyX2lkIjpudWxsLCJnZW5kZXJfaWQiOjEsImJpcnRoX3llYXIiOjE5NzgsImJpcnRoX2RhdGUiOiIxOTc4LTA4LTAxIiwicGhvbmUiOiI1OTk3MzgwMjMiLCJ1c2VyX25hbWUiOiJrYXhhIiwidXNlcl9zdXJuYW1lIjoibWlxZWxhZHplIiwidHlwZV9pZCI6MH19.DES3OMjLem3W0em42vnxoSEYOAq4jLEAjjjixvRyqDJT0bQHd30wFqqjSrSfGH9iLZkMp0gtrXiVFJGV_RlWTlTvwfQCVzZM4H58dS-nescI2DZy4CZdTF9u45nWtgxXxhnz9Kk0gbHaVtqXHu1rUnxLJQoGc9g1k0JSH_Y9xDPoBbsNmqivRu5E7BXkh2Q6eXXL6BuCxWRxaNeD7pJ8dQmrEt4HVOoqTvMD_TiHE-dvgf5RqQRK7q3JOd4f-niXIKwjgn1JCCU3WUPUhvjEiCR_lV-OmyB_3IHCxoDcNr7sT48fBvYYsYLOhrjZVbUNVdmPO0JZFUIskq_6vWG3dw',
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
                    
                    # The detail endpoint should return the property data directly
                    if data.get('result') and data.get('data'):
                        property_data = data['data']
                        self.logger.info(f"Successfully fetched property {property_id} in {language}")
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
