"""
API Key Management API Endpoints
Backend endpoints for the user dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from api.api_key_manager import api_key_manager
from api.admin_auth import verify_admin
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/keys", tags=["keys"])

class GenerateKeyRequest(BaseModel):
    tier: str
    prefix: Optional[str] = "key"

class DeactivateKeyRequest(BaseModel):
    key: str

verify_admin_key = verify_admin

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
            detail="Error listing keys"
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
            detail="Error generating key"
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
            detail="Error deactivating key"
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
            detail="Error getting key info"
        )

@router.get("/usage/{key}")
async def get_key_usage(
    key: str,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """Get usage statistics for a specific API key"""
    try:
        usage_data = api_key_manager.get_usage_stats(key)
        current_month = usage_data.get("month")
        key_info = api_key_manager.get_key_info(key)

        if not key_info:
            raise HTTPException(status_code=404, detail="Key not found")
        
        limit = key_info.get("requests_per_month", 100)
        used = usage_data.get("total_requests", 0)
        
        return {
            "success": True,
            "key": key[:20] + "...",
            "month": current_month,
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
            "percentage": (used / limit * 100) if limit > 0 else 0,
            "first_request": None,
            "last_request": usage_data.get("last_request"),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error getting usage"
        )

