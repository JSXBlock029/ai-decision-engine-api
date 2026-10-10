"""
Configuration for AI Decision Engine API
"""

import os
from typing import Dict, Any

class Config:
    """API Configuration"""
    
    # API Info
    API_NAME = "AI Decision Engine API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "RESTful API for AI-driven decision-making framework"
    
    # Server
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    
    # API Keys (in production, use database)
    API_KEYS: Dict[str, Dict[str, Any]] = {
        "dev_key_123": {
            "tier": "free",
            "requests_remaining": 100,
            "requests_limit": 100,
            "expires_at": None
        },
        "pro_key_456": {
            "tier": "pro",
            "requests_remaining": 10000,
            "requests_limit": 10000,
            "expires_at": None
        }
    }
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Database (for production)
    DATABASE_URL = os.getenv("DATABASE_URL", None)
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Feature Flags
    ENABLE_MEMORY_INSIGHTS = os.getenv("ENABLE_MEMORY_INSIGHTS", "True").lower() == "true"
    ENABLE_AUTONOMY_TRACKING = os.getenv("ENABLE_AUTONOMY_TRACKING", "True").lower() == "true"

