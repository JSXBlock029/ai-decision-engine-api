"""
Enhanced API utilities with input validation and sanitization
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re


def generate_api_key(prefix: str = "key") -> str:
    """Generate a secure API key"""
    import secrets
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"


def validate_api_key(api_key: str, valid_keys: Dict[str, Any]) -> bool:
    """Validate an API key"""
    return api_key in valid_keys


def format_api_response(data: Any, success: bool = True, message: Optional[str] = None) -> Dict[str, Any]:
    """Format API response consistently"""
    response = {
        "success": success,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    if message:
        response["message"] = message
    return response


def calculate_rate_limit_key(api_key: str, endpoint: str) -> str:
    """Calculate rate limit key for tracking"""
    key_string = f"{api_key}:{endpoint}"
    return hashlib.md5(key_string.encode()).hexdigest()


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user input to prevent injection attacks"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially harmful characters and limit length
            cleaned = re.sub(r'[<>"\']', '', value)
            sanitized[key] = cleaned.strip()[:1000]  # Limit length
        elif isinstance(value, (int, float)):
            sanitized[key] = value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_input(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    return sanitized


def validate_amount(amount: Any) -> float:
    """Validate and sanitize amount values"""
    try:
        amount_float = float(amount)
        if amount_float < 0:
            raise ValueError("Amount cannot be negative")
        if amount_float > 1e15:  # Reasonable upper limit
            raise ValueError("Amount exceeds maximum allowed")
        return amount_float
    except (ValueError, TypeError):
        raise ValueError("Invalid amount format")


def validate_category(category: str) -> str:
    """Validate decision category"""
    valid_categories = ["STRATEGIC", "OPERATIONAL", "FINANCIAL", "MARKETING", "RND", "COMPLIANCE"]
    category_upper = category.upper().strip()
    if category_upper not in valid_categories:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    return category_upper


def validate_risk_level(risk_level: str) -> str:
    """Validate risk level"""
    valid_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_upper = risk_level.upper().strip()
    if risk_upper not in valid_levels:
        raise ValueError(f"Invalid risk level. Must be one of: {', '.join(valid_levels)}")
    return risk_upper


def log_api_request(endpoint: str, method: str, api_key: Optional[str] = None, **kwargs):
    """Log API request for monitoring"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "api_key_prefix": api_key[:10] + "..." if api_key else None,
        **kwargs
    }
    # In production, this would write to a logging service
    return log_data


def create_error_response(error_message: str, error_code: str = "GENERIC_ERROR", status_code: int = 400) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": True,
        "error_code": error_code,
        "message": error_message,
        "timestamp": datetime.now().isoformat()
    }


def check_rate_limit(api_key: str, endpoint: str, rate_limits: Dict[str, int]) -> bool:
    """Check if request is within rate limits"""
    # Simplified rate limiting - in production, use Redis or similar
    # This is a placeholder for actual rate limiting logic
    return True
