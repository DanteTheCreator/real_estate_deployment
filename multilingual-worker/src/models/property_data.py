"""
Property data model for multilingual processing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PropertyData:
    """Data structure for property information with multilingual support."""
    
    # Identifiers
    external_id: Optional[str] = None
    
    # Georgian content (default)
    title: str = ""
    description: str = ""
    
    # English content
    title_en: Optional[str] = None
    description_en: Optional[str] = None
    
    # Russian content
    title_ru: Optional[str] = None
    description_ru: Optional[str] = None
    
    # Metadata
    source: str = 'myhome.ge'
    
    def has_multilingual_content(self) -> bool:
        """Check if property has any multilingual content."""
        return bool(
            self.title_en or self.title_ru or 
            self.description_en or self.description_ru
        )
    
    def is_complete_translation(self) -> bool:
        """Check if property has complete translations for both languages."""
        return bool(
            self.title_en and self.title_ru and
            self.description_en and self.description_ru
        )
