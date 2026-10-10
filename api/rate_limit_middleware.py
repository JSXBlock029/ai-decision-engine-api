"""
Rate Limiting Middleware
Enhanced rate limiting with Redis support (optional)
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import os

RATE_LIMIT_FILE = os.getenv("RATE_LIMIT_FILE", "rate_limits.json")
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app, default_limit: int = 60, window: int = 60):
        super().__init__(app)
        self.default_limit = default_limit  # requests per window
        self.window = window  # window in seconds
        self.rate_limits = self._load_limits()
    
    def _load_limits(self) -> Dict[str, Any]:
        """Load rate limit data"""
        try:
            if os.path.exists(RATE_LIMIT_FILE):
                with open(RATE_LIMIT_FILE, "r") as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {}
    
    def _save_limits(self):
        """Save rate limit data"""
        try:
            with open(RATE_LIMIT_FILE, "w") as f:
                json.dump(self.rate_limits, f, indent=2)
        except Exception:
            pass
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique key for rate limiting"""
        api_key = request.headers.get("X-API-Key", "anonymous")
        endpoint = request.url.path
        return f"{api_key}:{endpoint}"
    
    def _check_rate_limit(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        if not RATE_LIMIT_ENABLED:
            return True, {}
        
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window)
        
        if key not in self.rate_limits:
            self.rate_limits[key] = {
                "requests": [],
                "limit": self.default_limit
            }
        
        limit_data = self.rate_limits[key]
        
        # Remove old requests outside window
        limit_data["requests"] = [
            req_time for req_time in limit_data["requests"]
            if datetime.fromisoformat(req_time) > window_start
        ]
        
        # Check if limit exceeded
        if len(limit_data["requests"]) >= limit_data["limit"]:
            return False, {
                "limit": limit_data["limit"],
                "remaining": 0,
                "reset_at": (datetime.fromisoformat(limit_data["requests"][0]) + timedelta(seconds=self.window)).isoformat()
            }
        
        # Add current request
        limit_data["requests"].append(now.isoformat())
        self._save_limits()
        
        return True, {
            "limit": limit_data["limit"],
            "remaining": limit_data["limit"] - len(limit_data["requests"]),
            "reset_at": (now + timedelta(seconds=self.window)).isoformat()
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health endpoint
        if request.url.path == "/health":
            return await call_next(request)
        
        # Check rate limit
        client_key = self._get_client_key(request)
        allowed, limit_info = self._check_rate_limit(client_key)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit_info["limit"],
                    "reset_at": limit_info["reset_at"]
                },
                headers={
                    "X-RateLimit-Limit": str(limit_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": limit_info["reset_at"]
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = limit_info["reset_at"]
        
        return response

