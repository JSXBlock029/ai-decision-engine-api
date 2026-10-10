"""
System Monitoring & Status Dashboard
Real-time monitoring of AI Decision Engine systems
"""

from datetime import datetime
import json
import os
from typing import Dict, Any

class SystemMonitor:
    """Monitor all system components"""
    
    def __init__(self):
        self.status_file = "system_status.json"
        self.components = {
            "decision_engine": {"status": "unknown", "last_check": None},
            "memory_system": {"status": "unknown", "last_check": None},
            "autonomy_tracker": {"status": "unknown", "last_check": None},
            "api_service": {"status": "unknown", "last_check": None},
            "saas_landing": {"status": "unknown", "last_check": None},
            "income_strategies": {"status": "unknown", "last_check": None}
        }
    
    def check_decision_engine(self) -> bool:
        """Check if decision engine is working"""
        try:
            from ai_decision_engine import AIDecisionEngine
            engine = AIDecisionEngine()
            self.components["decision_engine"] = {
                "status": "operational",
                "last_check": datetime.now().isoformat()
            }
            return True
        except Exception as e:
            self.components["decision_engine"] = {
                "status": f"error: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
            return False
    
    def check_memory_system(self) -> bool:
        """Check if memory system is working"""
        try:
            if os.path.exists("ai_memory.json"):
                with open("ai_memory.json", "r") as f:
                    data = json.load(f)
                self.components["memory_system"] = {
                    "status": "operational",
                    "events": len(data.get("events", [])),
                    "decisions": len(data.get("decisions", [])),
                    "last_check": datetime.now().isoformat()
                }
                return True
            else:
                self.components["memory_system"] = {
                    "status": "no_memory_file",
                    "last_check": datetime.now().isoformat()
                }
                return False
        except Exception as e:
            self.components["memory_system"] = {
                "status": f"error: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
            return False
    
    def check_autonomy_tracker(self) -> bool:
        """Check if autonomy tracker is working"""
        try:
            from autonomy_tracker import GradualAutonomySystem
            autonomy = GradualAutonomySystem()
            level = autonomy.get_autonomy_level()
            self.components["autonomy_tracker"] = {
                "status": "operational",
                "autonomy_level": level,
                "last_check": datetime.now().isoformat()
            }
            return True
        except Exception as e:
            self.components["autonomy_tracker"] = {
                "status": f"error: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
            return False
    
    def check_api_service(self) -> bool:
        """Check if API service files exist"""
        api_files = [
            "api/main.py",
            "api/api_specification.yaml",
            "api/test_api.py"
        ]
        all_exist = all(os.path.exists(f) for f in api_files)
        self.components["api_service"] = {
            "status": "ready" if all_exist else "missing_files",
            "files": api_files,
            "all_present": all_exist,
            "last_check": datetime.now().isoformat()
        }
        return all_exist
    
    def check_saas_landing(self) -> bool:
        """Check if SaaS landing page exists"""
        landing_files = [
            "saas_landing/index.html",
            "saas_landing/waitlist_backend.py"
        ]
        all_exist = all(os.path.exists(f) for f in landing_files)
        self.components["saas_landing"] = {
            "status": "ready" if all_exist else "missing_files",
            "files": landing_files,
            "all_present": all_exist,
            "last_check": datetime.now().isoformat()
        }
        return all_exist
    
    def check_income_strategies(self) -> bool:
        """Check if income strategies are implemented"""
        try:
            from income_strategies import IncomeManager, APIServicesStrategy, SaaSProductStrategy
            manager = IncomeManager()
            self.components["income_strategies"] = {
                "status": "operational",
                "strategies_available": ["API_SERVICES", "SAAS_PRODUCT"],
                "last_check": datetime.now().isoformat()
            }
            return True
        except Exception as e:
            self.components["income_strategies"] = {
                "status": f"error: {str(e)}",
                "last_check": datetime.now().isoformat()
            }
            return False
    
    def check_all(self) -> Dict[str, Any]:
        """Check all system components"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        checks = [
            ("decision_engine", self.check_decision_engine),
            ("memory_system", self.check_memory_system),
            ("autonomy_tracker", self.check_autonomy_tracker),
            ("api_service", self.check_api_service),
            ("saas_landing", self.check_saas_landing),
            ("income_strategies", self.check_income_strategies)
        ]
        
        operational_count = 0
        for name, check_func in checks:
            try:
                is_ok = check_func()
                results["components"][name] = self.components[name]
                if is_ok:
                    operational_count += 1
            except Exception as e:
                results["components"][name] = {
                    "status": f"check_error: {str(e)}",
                    "last_check": datetime.now().isoformat()
                }
        
        results["summary"] = {
            "total_components": len(checks),
            "operational": operational_count,
            "status": "healthy" if operational_count == len(checks) else "degraded"
        }
        
        # Save status
        with open(self.status_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def print_status(self):
        """Print formatted status"""
        results = self.check_all()
        
        print("=" * 60)
        print("AI DECISION ENGINE - SYSTEM STATUS")
        print("=" * 60)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Overall Status: {results['summary']['status'].upper()}")
        print(f"Components Operational: {results['summary']['operational']}/{results['summary']['total_components']}")
        print()
        
        print("COMPONENT STATUS:")
        print("-" * 60)
        for name, info in results["components"].items():
            status = info.get("status", "unknown")
            status_icon = "✅" if "operational" in status or "ready" in status else "❌"
            print(f"{status_icon} {name.upper().replace('_', ' ')}: {status}")
            if "autonomy_level" in info:
                print(f"   Autonomy Level: {info['autonomy_level']}%")
            if "events" in info:
                print(f"   Events: {info.get('events', 0)}, Decisions: {info.get('decisions', 0)}")
        
        print()
        print("=" * 60)
        
        if results["summary"]["status"] == "healthy":
            print("✅ All systems operational!")
        else:
            print("⚠️  Some components need attention")

def main():
    """Run system monitoring"""
    monitor = SystemMonitor()
    monitor.print_status()

if __name__ == "__main__":
    main()

