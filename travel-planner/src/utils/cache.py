"""Simple caching system for web searches"""

import time
import hashlib
import json
from typing import Any, Optional


class SimpleCache:
    """In-memory cache with TTL"""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.cache = {}
        self.ttl = ttl
    
    def _get_key(self, data: Any) -> str:
        """Generate cache key from data"""
        try:
            serialized = json.dumps(data, sort_keys=True)
            return hashlib.md5(serialized.encode()).hexdigest()
        except (TypeError, ValueError):
            # Fallback for non-serializable data
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Get cached value if not expired
        
        Args:
            key: Cache key (any hashable data)
        
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._get_key(key)
        
        if cache_key in self.cache:
            timestamp, value = self.cache[cache_key]
            
            # Check if expired
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        return None
    
    def set(self, key: Any, value: Any):
        """
        Cache value with current timestamp
        
        Args:
            key: Cache key
            value: Value to cache
        """
        cache_key = self._get_key(key)
        self.cache[cache_key] = (time.time(), value)
    
    def clear(self):
        """Clear all cached values"""
        self.cache = {}
    
    def size(self) -> int:
        """Get number of cached items"""
        return len(self.cache)


# Global cache instance
search_cache = SimpleCache()

