"""
API Analytics Middleware
Tracks all API requests for analytics and marketing
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from api.analytics import api_analytics
from api.marketing_analytics import marketing_analytics
import logging

logger = logging.getLogger(__name__)

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to track API requests and marketing visits"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip analytics for health endpoint
        if request.url.path == "/health":
            return await call_next(request)
        
        # Track marketing visits (for non-API endpoints)
        if request.url.path in ["/", "/pricing", "/docs", "/payment/success"]:
            try:
                referer = request.headers.get("referer")
                user_agent = request.headers.get("user-agent")
                client_ip = request.client.host if request.client else None
                
                marketing_analytics.track_visit(
                    request_url=str(request.url),
                    referer=referer,
                    user_agent=user_agent,
                    ip_address=client_ip
                )
            except Exception as e:
                logger.error(f"Error tracking marketing visit: {e}")
        
        # Start timer
        start_time = time.time()
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key", "anonymous")
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Record analytics
        try:
            api_analytics.record_request(
                endpoint=request.url.path,
                method=request.method,
                api_key=api_key,
                status_code=response.status_code,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Error recording analytics: {e}")
        
        return response

