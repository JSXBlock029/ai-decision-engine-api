"""
Launch Preparation Script
Final checks before production launch
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class LaunchPreparer:
    """Prepare project for launch"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.checks = []
    
    def check_tests(self) -> bool:
        """Check if all tests pass"""
        print("Running tests...")
        try:
            result = subprocess.run(
                [sys.executable, "api/test_local.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[OK] All tests passing")
                return True
            else:
                print("[FAIL] Some tests failed")
                return False
        except Exception as e:
            print(f"[WARN] Could not run tests: {e}")
            return False
    
    def check_files(self) -> bool:
        """Check required files exist"""
        print("Checking required files...")
        required = [
            "api/main.py",
            "api/requirements.txt",
            "api/production_config.py",
            "saas_landing/index.html",
            ".gitignore"
        ]
        
        all_exist = True
        for file in required:
            path = self.project_root / file
            if path.exists():
                print(f"[OK] {file}")
            else:
                print(f"[FAIL] {file} missing")
                all_exist = False
        
        return all_exist
    
    def check_environment(self) -> bool:
        """Check environment setup"""
        print("Checking environment...")
        
        checks = {
            "Python": False,
            "Dependencies": False
        }
        
        # Check Python
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"[OK] Python: {result.stdout.strip()}")
                checks["Python"] = True
        except:
            print("[FAIL] Python not found")
        
        # Check dependencies
        try:
            import fastapi
            import uvicorn
            print("[OK] Dependencies installed")
            checks["Dependencies"] = True
        except ImportError:
            print("[FAIL] Dependencies not installed")
        
        return all(checks.values())
    
    def check_security(self) -> bool:
        """Check security configuration"""
        print("Checking security...")
        
        # Check .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if "api_keys.json" in content:
                print("[OK] API keys excluded from Git")
            else:
                print("[WARN] API keys may be committed")
        
        # Check for hardcoded secrets
        main_py = self.project_root / "api" / "main.py"
        if main_py.exists():
            content = main_py.read_text()
            if "change-me-in-production" not in content.lower():
                print("[OK] No default secrets found")
            else:
                print("[WARN] Default secrets may be present")
        
        return True
    
    def generate_launch_report(self) -> Dict[str, Any]:
        """Generate launch readiness report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "tests": self.check_tests(),
                "files": self.check_files(),
                "environment": self.check_environment(),
                "security": self.check_security()
            }
        }
        
        report["ready"] = all(report["checks"].values())
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print launch readiness report"""
        print("\n" + "=" * 60)
        print("LAUNCH READINESS REPORT")
        print("=" * 60)
        print()
        
        for check, passed in report["checks"].items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {check.replace('_', ' ').title()}")
        
        print()
        if report["ready"]:
            print("[SUCCESS] READY FOR LAUNCH!")
        else:
            print("[WARNING] Some checks failed. Review above.")
        print()

def main():
    """Run launch preparation"""
    preparer = LaunchPreparer()
    report = preparer.generate_launch_report()
    preparer.print_report(report)
    
    # Save report
    report_file = preparer.project_root / "launch_readiness_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: {report_file}")

if __name__ == "__main__":
    main()

