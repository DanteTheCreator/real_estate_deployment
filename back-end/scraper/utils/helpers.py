"""
Helper utility functions.
"""

import re
from typing import Any, Union


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default fallback."""
    if value is None:
        return default
    
    try:
        if isinstance(value, str):
            # Remove common suffixes and clean the string
            value = value.rstrip('+').strip()
            if not value or not value.replace('.', '').replace('-', '').replace(',', '').isdigit():
                return default
            # Remove commas (thousand separators)
            value = value.replace(',', '')
        
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default fallback."""
    if value is None:
        return default
    
    try:
        if isinstance(value, str):
            # Remove common suffixes and clean the string
            value = value.rstrip('+').strip()
            if not value:
                return default
            # Remove commas (thousand separators)
            value = value.replace(',', '')
        
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """Safely convert value to bool with default fallback."""
    if value is None:
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    return default


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and standardizing format."""
    if not text:
        return ""
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters
    normalized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', normalized)
    
    return normalized


def clean_address(address: str) -> str:
    """Clean and normalize address string."""
    if not address:
        return ""
    
    # Normalize text first
    cleaned = normalize_text(address)
    
    # Remove common prefixes/suffixes
    prefixes_to_remove = ['address:', 'addr:', 'location:']
    for prefix in prefixes_to_remove:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    
    # Capitalize first letter of each word
    cleaned = ' '.join(word.capitalize() for word in cleaned.split())
    
    return cleaned


def extract_numbers(text: str) -> list:
    """Extract all numbers from text string."""
    if not text:
        return []
    
    # Find all numeric patterns (including decimals)
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(num) if '.' in num else int(num) for num in numbers]


def truncate_text(text: str, max_length: int = 255, suffix: str = "...") -> str:
    """Truncate text to specified length with optional suffix."""
    if not text or len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def format_currency(amount: float, currency: str = "GEL") -> str:
    """Format currency amount with proper symbol."""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GEL': '₾'
    }
    
    symbol = currency_symbols.get(currency.upper(), currency)
    
    if currency.upper() == 'GEL':
        return f"{amount:,.0f} {symbol}"
    else:
        return f"{symbol}{amount:,.0f}"


def parse_area_string(area_str: str) -> tuple:
    """Parse area string to extract numeric value and unit."""
    if not area_str:
        return 0.0, "sqm"
    
    # Extract numbers and units
    match = re.search(r'(\d+\.?\d*)\s*(\w+)?', str(area_str))
    if match:
        value = float(match.group(1))
        unit = match.group(2) or "sqm"
        return value, unit.lower()
    
    return 0.0, "sqm"


def validate_email(email: str) -> bool:
    """Simple email validation."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Simple phone number validation."""
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it contains only digits and is reasonable length
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def generate_property_slug(title: str, property_id: str) -> str:
    """Generate URL-friendly slug from property title and ID."""
    if not title:
        return f"property-{property_id}"
    
    # Convert to lowercase
    slug = title.lower()
    
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    slug = truncate_text(slug, 50, "")
    
    # Add property ID for uniqueness
    return f"{slug}-{property_id}"


def calculate_price_per_sqm(total_price: float, area_sqm: float) -> float:
    """Calculate price per square meter."""
    if area_sqm <= 0:
        return 0.0
    
    return total_price / area_sqm


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
