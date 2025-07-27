"""
Parameter and amenity processing.
"""

import logging
from typing import Dict, List
import aiohttp

from sqlalchemy.orm import Session

# Import with fallbacks for Docker compatibility
try:
    from core.config import ScrapingConfig
    from models.property_data import PropertyData, PropertyParameter
except ImportError:
    try:
        from ..core.config import ScrapingConfig
        from ..models.property_data import PropertyData, PropertyParameter
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.models.property_data import PropertyData, PropertyParameter


class ParameterProcessor:
    """Handles property parameters and amenities processing."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the parameter processor."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_property_parameters(self, 
                                     property_data: PropertyData, 
                                     raw_data: Dict) -> None:
        """Process property parameters/amenities from API response."""
        try:
            parameters_data = raw_data.get('parameters', [])
            if not parameters_data:
                self.logger.debug(f"No parameters found for property {property_data.external_id}")
                return
            
            self.logger.debug(f"Processing {len(parameters_data)} parameters for property {property_data.external_id}")
            
            for param_data in parameters_data:
                if not isinstance(param_data, dict):
                    continue
                
                param_external_id = param_data.get('id')  # This is the external_id from API
                param_key = param_data.get('key')
                display_name = param_data.get('display_name')
                param_value = param_data.get('parameter_value')
                
                if not param_external_id or not param_key:
                    continue
                
                # Create PropertyParameter object using the external_id from the API
                # The database service will handle the mapping to internal parameter ID
                property_parameter = PropertyParameter(
                    parameter_id=param_external_id,  # This will be treated as external_id by database service
                    parameter_value=param_value,  # Use the parameter value from API
                    parameter_select_name=display_name  # Use display name as select name
                )
                
                property_data.parameters.append(property_parameter)
                self.logger.debug(f"Added parameter: {param_key} (external_id: {param_external_id}) for property {property_data.external_id}")
            
            self.logger.debug(f"Successfully processed {len(property_data.parameters)} parameters for property {property_data.external_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing parameters for property {property_data.external_id}: {e}")
            # Don't raise the exception - continue processing without parameters

    def get_parameter_by_key(self, property_data: PropertyData, parameter_key: str) -> str:
        """Get parameter value by key (requires database lookup)."""
        # This would require database access to resolve parameter keys
        # For now, return empty string
        return ""
    
    def get_amenities_list(self, property_data: PropertyData) -> List[str]:
        """Get list of amenity names (requires database lookup)."""
        # This would require database access to resolve parameter names
        # For now, return empty list
        return []
    
    def has_amenity(self, property_data: PropertyData, amenity_name: str) -> bool:
        """Check if property has specific amenity."""
        amenities = self.get_amenities_list(property_data)
        return amenity_name.lower() in [a.lower() for a in amenities]
