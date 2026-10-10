"""
API Response Caching
Improves performance by caching frequently accessed data
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os

CACHE_FILE = "api_cache.json"
CACHE_TTL = 300  # 5 minutes default

class ResponseCache:
    """Cache API responses for performance"""
    
    def __init__(self, ttl: int = CACHE_TTL):
        self.cache_file = CACHE_FILE
        self.ttl = ttl
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def _generate_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key from endpoint and parameters"""
        key_string = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached response if available and not expired"""
        cache_key = self._generate_key(endpoint, params)
        
        if cache_key not in self.cache:
            return None
        
        cached_item = self.cache[cache_key]
        cached_time = datetime.fromisoformat(cached_item["timestamp"])
        
        # Check if expired
        if datetime.now() - cached_time > timedelta(seconds=self.ttl):
            del self.cache[cache_key]
            self._save_cache()
            return None
        
        return cached_item["data"]
    
    def set(self, endpoint: str, params: Dict[str, Any], data: Any):
        """Cache a response"""
        cache_key = self._generate_key(endpoint, params)
        
        self.cache[cache_key] = {
            "endpoint": endpoint,
            "params": params,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Limit cache size (keep last 100 items)
        if len(self.cache) > 100:
            # Remove oldest items
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            for key, _ in sorted_items[:-100]:
                del self.cache[key]
        
        self._save_cache()
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
        self._save_cache()
    
    def clear_endpoint(self, endpoint: str):
        """Clear cache for specific endpoint"""
        keys_to_remove = [
            key for key, value in self.cache.items()
            if value.get("endpoint") == endpoint
        ]
        for key in keys_to_remove:
            del self.cache[key]
        self._save_cache()

# Global cache instance
response_cache = ResponseCache()

