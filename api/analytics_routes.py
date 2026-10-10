"""
API Analytics Endpoint
Provides analytics data via API
"""

from fastapi import APIRouter, Depends, HTTPException
from api.analytics import api_analytics
from api.admin_auth import verify_admin
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

verify_admin_key = verify_admin

@router.get("/stats", response_model=Dict[str, Any])
async def get_analytics_stats(
    days: int = 30,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """
    Get API analytics statistics
    
    - **days**: Number of days to analyze (default: 30)
    - Requires the admin key (X-Admin-Key)
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
            detail="Error generating analytics"
        )

@router.get("/endpoint/{endpoint_path:path}", response_model=Dict[str, Any])
async def get_endpoint_stats(
    endpoint_path: str,
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """
    Get statistics for a specific endpoint
    
    - **endpoint_path**: Path of the endpoint (e.g., "/decisions/evaluate")
    - Requires the admin key (X-Admin-Key)
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
            detail="Error getting endpoint stats"
        )

@router.post("/export", response_model=Dict[str, Any])
async def export_analytics_report(
    api_info: Dict[str, Any] = Depends(verify_admin_key)
):
    """
    Export analytics report as JSON
    
    - Requires the admin key (X-Admin-Key)
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
            detail="Error exporting report"
        )

