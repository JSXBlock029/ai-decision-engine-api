"""
API Versioning
Support for multiple API versions
"""

from fastapi import APIRouter
from typing import Dict, Any

# API Version
API_VERSION = "v1"

def create_versioned_router(version: str = API_VERSION) -> APIRouter:
    """Create a versioned API router"""
    return APIRouter(prefix=f"/{version}")

def get_api_version(request) -> str:
    """Extract API version from request"""
    # Check header first
    version_header = request.headers.get("X-API-Version", API_VERSION)
    
    # Check URL path
    path_parts = request.url.path.split("/")
    if len(path_parts) > 1 and path_parts[1].startswith("v"):
        return path_parts[1]
    
    return version_header or API_VERSION

def version_response(data: Dict[str, Any], version: str = API_VERSION) -> Dict[str, Any]:
    """Add version info to response"""
    return {
        **data,
        "api_version": version,
        "version_info": {
            "current": version,
            "latest": API_VERSION,
            "deprecated": False
        }
    }

