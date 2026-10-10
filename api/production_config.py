"""
Production configuration for AI Decision Engine API
Environment variables should be set in production
"""

import os
from typing import List

class ProductionConfig:
    """Production configuration settings"""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "https://example.com,https://www.example.com"
    ).split(",")
    
    # Database (for production)
    DATABASE_URL = os.getenv("DATABASE_URL", None)
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "api.log")
    
    # Monitoring
    ENABLE_MONITORING = os.getenv("ENABLE_MONITORING", "True").lower() == "true"
    MONITORING_ENDPOINT = os.getenv("MONITORING_ENDPOINT", None)
    
    # Feature Flags
    ENABLE_MEMORY_INSIGHTS = os.getenv("ENABLE_MEMORY_INSIGHTS", "True").lower() == "true"
    ENABLE_AUTONOMY_TRACKING = os.getenv("ENABLE_AUTONOMY_TRACKING", "True").lower() == "true"
    
    # SSL/TLS
    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", None)
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", None)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.ALLOWED_ORIGINS:
            errors.append("ALLOWED_ORIGINS must be set")
        
        if cls.DEBUG and os.getenv("ENVIRONMENT") == "production":
            errors.append("DEBUG should be False in production")
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == "change-me-in-production":
            errors.append("SECRET_KEY must be changed in production")
        
        return errors

