"""
Price processing and currency handling.
"""

import logging
from typing import Dict, Tuple, List

# Import with fallbacks for Docker compatibility
try:
    from core.config import ScrapingConfig
    from models.property_data import PropertyData, PropertyPrice
except ImportError:
    try:
        from ..core.config import ScrapingConfig
        from ..models.property_data import PropertyData, PropertyPrice
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.models.property_data import PropertyData, PropertyPrice


class PriceProcessor:
    """Handles property price processing from API data."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the price processor."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_property_prices(self, property_data: PropertyData, raw_data: Dict) -> None:
        """Process property prices and convert currencies."""
        try:
            price_data = raw_data.get('price', {})
            if not price_data:
                self.logger.debug(f"No price data found for property {property_data.external_id}")
                return
            
            # Track primary prices for main fields
            gel_price = None
            usd_price = None
            
            # Process each currency
            for currency_id, price_info in price_data.items():
                if not price_info or not price_info.get('price_total'):
                    continue
                
                try:
                    currency_int = int(currency_id)
                    currency = self.config.currency_types.get(currency_int, 'USD')
                    price_total = float(price_info['price_total'])
                    price_square = float(price_info.get('price_square', 0))
                    
                    # Track primary amounts for main fields
                    # NOTE: API currency mappings appear to be reversed from expected
                    if currency_int == 1:  # API says USD but contains GEL values
                        gel_price = price_total
                    elif currency_int == 2:  # API says GEL but contains USD values  
                        usd_price = price_total
                    
                    # Add price record to separate prices table
                    property_data.add_price(
                        currency_type=currency_id,
                        price_total=price_total,
                        price_square=price_square
                    )
                    
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Error processing price in currency {currency_id}: {e}")
                    continue
            
            # Set main rent amount fields in properties table
            if gel_price is not None:
                property_data.rent_amount = gel_price
            if usd_price is not None:
                property_data.rent_amount_usd = usd_price
            
            # If we only have one currency, convert to the other
            if gel_price is not None and usd_price is None:
                # Convert GEL to USD
                property_data.rent_amount_usd = round(gel_price / 2.7, 2)
            elif usd_price is not None and gel_price is None:
                # Convert USD to GEL
                property_data.rent_amount = round(usd_price * 2.7, 2)
            elif gel_price is None and usd_price is None:
                # No valid prices found
                property_data.rent_amount = 0
                property_data.rent_amount_usd = 0
                
            self.logger.debug(f"Processed prices for property {property_data.external_id}: GEL={gel_price}, USD={usd_price}")
            
            self.logger.debug(f"Processed {len(property_data.prices)} price records for property {property_data.external_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing prices for property {property_data.external_id}: {e}")
    
    def get_price_in_currency(self, property_data: PropertyData, target_currency: str) -> float:
        """Get property price in target currency."""
        # Check if we have direct price in target currency
        for price in property_data.prices:
            currency = self.config.currency_types.get(int(price.currency_type), 'USD')
            if currency == target_currency:
                return price.price_total
        
        # Return primary amounts
        if target_currency == 'GEL':
            return property_data.rent_amount
        elif target_currency == 'USD':
            return property_data.rent_amount_usd
        else:
            # Return 0 for unsupported currencies
            return 0.0
    
    def get_price_summary(self, property_data: PropertyData) -> Dict[str, float]:
        """Get summary of all available prices."""
        summary = {}
        
        for price in property_data.prices:
            currency = self.config.currency_types.get(int(price.currency_type), 'USD')
            summary[currency] = price.price_total
        
        return summary
