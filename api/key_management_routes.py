"""
API Key Management API Endpoints
Backend endpoints for the user dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from api.api_key_manager import api_key_manager
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/keys", tags=["keys"])

class GenerateKeyRequest(BaseModel):
    tier: str
    prefix: Optional[str] = "key"

class DeactivateKeyRequest(BaseModel):
    key: str

def verify_admin_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Dict[str, Any]:
    """Verify admin API key"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    key_info = api_key_manager.validate_api_key(x_api_key)
    if not key_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Allow dev/pro/enterprise tiers for key management
    tier = key_info.get("tier", "").lower()
    if tier not in ["dev", "pro", "enterprise"]:
        raise HTTPException(
            status_code=403,
            detail="Key management requires Dev, Pro, or Enterprise tier"
        )
    
    return key_info

@router.get("/list")
async def list_keys(api_info: Dict[str, Any] = Depends(verify_admin_key)):
    """List all API keys (admin function)"""
    try:
        keys = api_key_manager.list_keys()
        return {
            "success": True,
            "keys": keys,
            "count": len(keys),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing keys: {str(e)}"
        )

@router.post("/generate")
async def generate_key(
    request: GenerateKeyRequest,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """Generate a new API key"""
    try:
        api_key = api_key_manager.generate_api_key(
            tier=request.tier,
            prefix=request.prefix
        )
        
        key_info = api_key_manager.get_key_info(api_key)
        
        return {
            "success": True,
            "key": api_key,
            "tier": request.tier,
            "requests_per_month": key_info.get("requests_per_month"),
            "created_at": key_info.get("created_at"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating key: {str(e)}"
        )

@router.post("/deactivate")
async def deactivate_key(
    request: DeactivateKeyRequest,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """Deactivate an API key"""
    try:
        success = api_key_manager.deactivate_key(request.key)
        
        if success:
            return {
                "success": True,
                "message": "Key deactivated successfully",
                "key": request.key[:20] + "...",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Key not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deactivating key: {str(e)}"
        )

@router.get("/info/{key}")
async def get_key_info(
    key: str,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """Get information about a specific API key"""
    try:
        key_info = api_key_manager.get_key_info(key)
        
        if not key_info:
            raise HTTPException(
                status_code=404,
                detail="Key not found"
            )
        
        return {
            "success": True,
            "key": key[:20] + "...",
            "info": key_info,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting key info: {str(e)}"
        )

@router.get("/usage/{key}")
async def get_key_usage(
    key: str,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """Get usage statistics for a specific API key"""
    try:
        import json
        import os
        
        # Load rate limits
        rate_limit_file = os.getenv("RATE_LIMIT_FILE", "rate_limits.json")
        try:
            with open(rate_limit_file, "r") as f:
                rate_limits = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            rate_limits = {}
        
        # Get current month usage
        current_month = datetime.now().strftime("%Y-%m")
        month_key = f"{key}_{current_month}"
        
        usage_data = rate_limits.get(month_key, {})
        key_info = api_key_manager.get_key_info(key)
        
        if not key_info:
            raise HTTPException(status_code=404, detail="Key not found")
        
        limit = key_info.get("requests_per_month", 100)
        used = usage_data.get("count", 0)
        
        return {
            "success": True,
            "key": key[:20] + "...",
            "month": current_month,
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
            "percentage": (used / limit * 100) if limit > 0 else 0,
            "first_request": usage_data.get("first_request"),
            "last_request": usage_data.get("last_request"),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting usage: {str(e)}"
        )

