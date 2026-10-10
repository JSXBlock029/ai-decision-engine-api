"""
Marketing Analytics
Track traffic sources, UTM parameters, and marketing campaign performance
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

MARKETING_ANALYTICS_FILE = os.getenv("MARKETING_ANALYTICS_FILE", "marketing_analytics.json")


class MarketingAnalytics:
    """Track marketing campaigns and traffic sources"""
    
    def __init__(self):
        self.analytics_file = MARKETING_ANALYTICS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure analytics file exists"""
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, "w") as f:
                json.dump({
                    "visits": [],
                    "signups": [],
                    "by_source": {},
                    "by_campaign": {},
                    "daily_stats": {},
                    "conversion_funnel": {
                        "visitors": 0,
                        "signups": 0,
                        "api_users": 0,
                        "paying_customers": 0
                    }
                }, f, indent=2)
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data"""
        try:
            with open(self.analytics_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "visits": [],
                "signups": [],
                "by_source": {},
                "by_campaign": {},
                "daily_stats": {},
                "conversion_funnel": {
                    "visitors": 0,
                    "signups": 0,
                    "api_users": 0,
                    "paying_customers": 0
                }
            }
    
    def _save_analytics(self, data: Dict[str, Any]):
        """Save analytics data"""
        with open(self.analytics_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def track_visit(self, request_url: str, referer: Optional[str] = None, 
                   user_agent: Optional[str] = None, ip_address: Optional[str] = None):
        """Track a website visit with UTM parameters"""
        data = self._load_analytics()
        
        # Parse UTM parameters from URL
        parsed_url = urlparse(request_url)
        query_params = parse_qs(parsed_url.query)
        
        utm_source = query_params.get("utm_source", ["direct"])[0]
        utm_medium = query_params.get("utm_medium", ["none"])[0]
        utm_campaign = query_params.get("utm_campaign", ["none"])[0]
        utm_term = query_params.get("utm_term", [""])[0]
        utm_content = query_params.get("utm_content", [""])[0]
        
        # Determine source from referer if no UTM
        if utm_source == "direct" and referer:
            # Parse referer domain
            try:
                referer_domain = urlparse(referer).netloc
                if "reddit.com" in referer_domain:
                    utm_source = "reddit"
                    utm_medium = "social"
                elif "news.ycombinator.com" in referer_domain:
                    utm_source = "hackernews"
                    utm_medium = "social"
                elif "twitter.com" in referer_domain or "x.com" in referer_domain:
                    utm_source = "twitter"
                    utm_medium = "social"
                elif "producthunt.com" in referer_domain:
                    utm_source = "producthunt"
                    utm_medium = "social"
                elif "indiehackers.com" in referer_domain:
                    utm_source = "indiehackers"
                    utm_medium = "social"
                elif "dev.to" in referer_domain:
                    utm_source = "devto"
                    utm_medium = "social"
            except:
                pass
        
        visit_record = {
            "timestamp": datetime.now().isoformat(),
            "url": request_url,
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
            "utm_term": utm_term,
            "utm_content": utm_content,
            "referer": referer,
            "user_agent": user_agent,
            "ip_address": ip_address
        }
        
        # Add to visits list (keep last 5000)
        data["visits"].append(visit_record)
        if len(data["visits"]) > 5000:
            data["visits"] = data["visits"][-5000:]
        
        # Update by_source stats
        if utm_source not in data["by_source"]:
            data["by_source"][utm_source] = {
                "visits": 0,
                "signups": 0,
                "api_users": 0,
                "paying_customers": 0,
                "revenue": 0
            }
        
        data["by_source"][utm_source]["visits"] += 1
        
        # Update by_campaign stats
        campaign_key = f"{utm_source}_{utm_campaign}"
        if campaign_key not in data["by_campaign"]:
            data["by_campaign"][campaign_key] = {
                "visits": 0,
                "signups": 0,
                "api_users": 0,
                "paying_customers": 0,
                "revenue": 0
            }
        
        data["by_campaign"][campaign_key]["visits"] += 1
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["daily_stats"]:
            data["daily_stats"][today] = {
                "visits": 0,
                "signups": 0,
                "by_source": {}
            }
        
        data["daily_stats"][today]["visits"] += 1
        if utm_source not in data["daily_stats"][today]["by_source"]:
            data["daily_stats"][today]["by_source"][utm_source] = 0
        data["daily_stats"][today]["by_source"][utm_source] += 1
        
        # Update conversion funnel
        data["conversion_funnel"]["visitors"] += 1
        
        self._save_analytics(data)
        return visit_record
    
    def track_signup(self, api_key: str, utm_source: Optional[str] = None, 
                    utm_campaign: Optional[str] = None):
        """Track a new signup"""
        data = self._load_analytics()
        
        signup_record = {
            "timestamp": datetime.now().isoformat(),
            "api_key_prefix": api_key[:10] + "..." if api_key else "unknown",
            "utm_source": utm_source or "unknown",
            "utm_campaign": utm_campaign or "unknown"
        }
        
        data["signups"].append(signup_record)
        if len(data["signups"]) > 1000:
            data["signups"] = data["signups"][-1000:]
        
        # Update by_source stats
        if utm_source and utm_source in data["by_source"]:
            data["by_source"][utm_source]["signups"] += 1
        
        # Update by_campaign stats
        if utm_source and utm_campaign:
            campaign_key = f"{utm_source}_{utm_campaign}"
            if campaign_key in data["by_campaign"]:
                data["by_campaign"][campaign_key]["signups"] += 1
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today in data["daily_stats"]:
            data["daily_stats"][today]["signups"] = data["daily_stats"][today].get("signups", 0) + 1
        
        # Update conversion funnel
        data["conversion_funnel"]["signups"] += 1
        
        self._save_analytics(data)
        return signup_record
    
    def get_marketing_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get marketing statistics"""
        data = self._load_analytics()
        
        # Calculate date range
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Filter recent visits
        recent_visits = [
            v for v in data.get("visits", [])
            if v.get("timestamp", "") >= cutoff_date
        ]
        
        # Filter recent signups
        recent_signups = [
            s for s in data.get("signups", [])
            if s.get("timestamp", "") >= cutoff_date
        ]
        
        # Calculate conversion rates
        total_visits = len(recent_visits)
        total_signups = len(recent_signups)
        conversion_rate = (total_signups / total_visits * 100) if total_visits > 0 else 0
        
        # Get top sources
        source_stats = {}
        for source, stats in data.get("by_source", {}).items():
            source_stats[source] = {
                "visits": stats.get("visits", 0),
                "signups": stats.get("signups", 0),
                "conversion_rate": (stats.get("signups", 0) / stats.get("visits", 1) * 100) if stats.get("visits", 0) > 0 else 0,
                "api_users": stats.get("api_users", 0),
                "paying_customers": stats.get("paying_customers", 0),
                "revenue": stats.get("revenue", 0)
            }
        
        return {
            "period_days": days,
            "total_visits": total_visits,
            "total_signups": total_signups,
            "overall_conversion_rate": round(conversion_rate, 2),
            "by_source": source_stats,
            "conversion_funnel": data.get("conversion_funnel", {}),
            "daily_stats": data.get("daily_stats", {})
        }
    
    def get_top_sources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing traffic sources"""
        data = self._load_analytics()
        
        sources = []
        for source, stats in data.get("by_source", {}).items():
            sources.append({
                "source": source,
                "visits": stats.get("visits", 0),
                "signups": stats.get("signups", 0),
                "conversion_rate": round((stats.get("signups", 0) / stats.get("visits", 1) * 100) if stats.get("visits", 0) > 0 else 0, 2),
                "api_users": stats.get("api_users", 0),
                "paying_customers": stats.get("paying_customers", 0),
                "revenue": stats.get("revenue", 0)
            })
        
        return sorted(sources, key=lambda x: x["visits"], reverse=True)[:limit]


# Global instance
marketing_analytics = MarketingAnalytics()

