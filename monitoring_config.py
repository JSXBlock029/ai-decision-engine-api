"""
Monitoring Configuration
Set up monitoring and alerting for production
"""

import json
from typing import Dict, Any, List
from datetime import datetime

class MonitoringConfig:
    """Configuration for monitoring and alerting"""
    
    def __init__(self):
        self.config_file = "monitoring_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default = {
            "enabled": True,
            "alerts": {
                "error_rate_threshold": 5.0,  # 5% error rate
                "response_time_threshold": 1000,  # 1 second
                "uptime_threshold": 99.0,  # 99% uptime
                "rate_limit_warning": 80  # Warn at 80% of limit
            },
            "endpoints": {
                "health_check_interval": 60,  # seconds
                "health_check_url": "/health",
                "expected_response_time": 100  # ms
            },
            "notifications": {
                "email": [],
                "webhook": [],
                "slack": None
            },
            "metrics": {
                "retention_days": 30,
                "aggregation_interval": 300  # 5 minutes
            }
        }
        
        try:
            import os
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    loaded = json.load(f)
                    default.update(loaded)
        except:
            pass
        
        return default
    
    def save_config(self):
        """Save monitoring configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def get_alert_thresholds(self) -> Dict[str, float]:
        """Get alert thresholds"""
        return self.config.get("alerts", {})
    
    def add_notification_email(self, email: str):
        """Add email for notifications"""
        if "email" not in self.config["notifications"]:
            self.config["notifications"]["email"] = []
        if email not in self.config["notifications"]["email"]:
            self.config["notifications"]["email"].append(email)
        self.save_config()
    
    def add_webhook(self, url: str):
        """Add webhook for notifications"""
        if "webhook" not in self.config["notifications"]:
            self.config["notifications"]["webhook"] = []
        if url not in self.config["notifications"]["webhook"]:
            self.config["notifications"]["webhook"].append(url)
        self.save_config()

# Monitoring service recommendations
MONITORING_SERVICES = {
    "uptime": [
        "UptimeRobot (free tier available)",
        "Pingdom",
        "StatusCake"
    ],
    "errors": [
        "Sentry (free tier available)",
        "Rollbar",
        "Bugsnag"
    ],
    "analytics": [
        "Google Analytics",
        "Mixpanel",
        "Amplitude"
    ],
    "logs": [
        "Loggly",
        "Papertrail",
        "Datadog"
    ]
}

def print_monitoring_setup():
    """Print monitoring setup guide"""
    print("=" * 60)
    print("MONITORING SETUP GUIDE")
    print("=" * 60)
    print()
    print("Recommended Services:")
    print()
    for category, services in MONITORING_SERVICES.items():
        print(f"{category.upper()}:")
        for service in services:
            print(f"  - {service}")
        print()

if __name__ == "__main__":
    config = MonitoringConfig()
    print_monitoring_setup()
    print(f"Configuration saved to: {config.config_file}")

