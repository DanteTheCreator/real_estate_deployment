"""
Redis caching utilities for improved performance
"""
import json
import redis
from typing import Optional, Any, List
from config import settings
import logging
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    CACHE_ENABLED = True
    logger.info("✅ Redis cache enabled")
except Exception as e:
    logger.warning(f"❌ Redis not available, cache disabled: {e}")
    redis_client = None
    CACHE_ENABLED = False


class CacheManager:
    """Redis cache manager for property queries"""
    
    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        """Generate a cache key from parameters"""
        # Sort kwargs for consistent key generation
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        hash_key = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if not CACHE_ENABLED:
            return None
        
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (default 5 minutes)"""
        if not CACHE_ENABLED:
            return False
        
        try:
            redis_client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        if not CACHE_ENABLED:
            return False
        
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """Clear cache keys matching pattern"""
        if not CACHE_ENABLED:
            return 0
        
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
        
        return 0


def cache_property_search(ttl: int = 300):
    """Decorator for caching property search results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Generate cache key from function parameters
            cache_key = CacheManager.generate_cache_key(
                f"property_search:{func.__name__}",
                **kwargs
            )
            
            # Try to get from cache
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        return wrapper
    return decorator


def invalidate_property_cache(property_id: Optional[int] = None):
    """Invalidate property-related cache entries"""
    if not CACHE_ENABLED:
        return
    
    patterns_to_clear = [
        "property_search:*",
        "property_count:*",
        "featured_properties:*"
    ]
    
    if property_id:
        patterns_to_clear.append(f"property:{property_id}:*")
    
    for pattern in patterns_to_clear:
        count = CacheManager.clear_pattern(pattern)
        if count > 0:
            logger.info(f"Cleared {count} cache entries for pattern: {pattern}")


# Cache configuration
CACHE_TTL = {
    'property_search': 300,      # 5 minutes
    'property_count': 600,       # 10 minutes  
    'featured_properties': 900,  # 15 minutes
    'property_detail': 1800,     # 30 minutes
}
