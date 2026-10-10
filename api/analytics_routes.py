"""
API Analytics Endpoint
Provides analytics data via API
"""

from fastapi import APIRouter, Depends, HTTPException
from api.analytics import api_analytics
from api.api_key_manager import api_key_manager
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

def verify_admin_key(x_api_key: Optional[str] = None) -> Dict[str, Any]:
    """Verify admin API key for analytics access"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    key_info = api_key_manager.validate_api_key(x_api_key)
    if not key_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Only allow pro/enterprise tiers to access analytics
    tier = key_info.get("tier", "").lower()
    if tier not in ["pro", "enterprise", "dev"]:
        raise HTTPException(
            status_code=403,
            detail="Analytics access requires Pro or Enterprise tier"
        )
    
    return key_info

@router.get("/stats", response_model=Dict[str, Any])
async def get_analytics_stats(
    days: int = 30,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """
    Get API analytics statistics
    
    - **days**: Number of days to analyze (default: 30)
    - Requires Pro or Enterprise tier API key
    """
    try:
        stats = api_analytics.get_stats(days=days)
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analytics: {str(e)}"
        )

@router.get("/endpoint/{endpoint_path:path}", response_model=Dict[str, Any])
async def get_endpoint_stats(
    endpoint_path: str,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """
    Get statistics for a specific endpoint
    
    - **endpoint_path**: Path of the endpoint (e.g., "/decisions/evaluate")
    - Requires Pro or Enterprise tier API key
    """
    try:
        stats = api_analytics.get_endpoint_stats(endpoint_path)
        return {
            "success": True,
            "endpoint": endpoint_path,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting endpoint stats: {str(e)}"
        )

@router.post("/export", response_model=Dict[str, Any])
async def export_analytics_report(
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """
    Export analytics report as JSON
    
    - Requires Pro or Enterprise tier API key
    """
    try:
        report = api_analytics.export_report()
        return {
            "success": True,
            "message": "Report exported to api_analytics_report.json",
            "data": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting report: {str(e)}"
        )

