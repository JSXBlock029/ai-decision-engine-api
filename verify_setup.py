"""
Setup Verification Script
Verifies all components are properly configured
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> tuple[bool, str]:
    """Check if a file exists"""
    if os.path.exists(filepath):
        return True, f"✅ {description}"
    return False, f"❌ {description} - NOT FOUND"

def check_directory_exists(dirpath: str, description: str) -> tuple[bool, str]:
    """Check if a directory exists"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        return True, f"✅ {description}"
    return False, f"❌ {description} - NOT FOUND"

def check_json_valid(filepath: str, description: str) -> tuple[bool, str]:
    """Check if JSON file is valid"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, f"✅ {description} - Valid JSON"
        return False, f"❌ {description} - File not found"
    except json.JSONDecodeError as e:
        return False, f"❌ {description} - Invalid JSON: {e}"
    except Exception as e:
        return False, f"❌ {description} - Error: {e}"

def check_python_import(module: str, description: str) -> tuple[bool, str]:
    """Check if Python module can be imported"""
    try:
        __import__(module)
        return True, f"✅ {description}"
    except ImportError as e:
        return False, f"❌ {description} - Import error: {e}"

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("AI DECISION ENGINE - SETUP VERIFICATION")
    print("=" * 70)
    print()
    
    base_path = Path(__file__).parent
    
    checks = []
    
    # Core system files
    print("📁 Core System Files:")
    print("-" * 70)
    core_files = [
        ("ai_decision_engine.py", "Decision Engine"),
        ("income_strategies.py", "Income Strategies"),
        ("ai_memory_system.py", "Memory System"),
        ("autonomy_tracker.py", "Autonomy Tracker"),
        ("run_system.py", "Main Runner"),
        ("START_HERE.md", "Startup Guide"),
        ("PROGRESS_STATUS.json", "Progress Tracking"),
    ]
    
    for filename, desc in core_files:
        result = check_file_exists(str(base_path / filename), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # API files
    print("🌐 API Service Files:")
    print("-" * 70)
    api_files = [
        ("api/main.py", "API Server"),
        ("api/api_specification.yaml", "API Specification"),
        ("api/test_api.py", "API Tests"),
        ("api/config.py", "API Config"),
        ("api/utils.py", "API Utils"),
        ("api/Dockerfile", "Docker Config"),
        ("api/docker-compose.yml", "Docker Compose"),
    ]
    
    for filepath, desc in api_files:
        result = check_file_exists(str(base_path / filepath), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # SaaS files
    print("💼 SaaS Landing Files:")
    print("-" * 70)
    saas_files = [
        ("saas_landing/index.html", "Landing Page"),
        ("saas_landing/waitlist_backend.py", "Waitlist Backend"),
        ("saas_landing/update_landing_api.js", "Frontend JS"),
    ]
    
    for filepath, desc in saas_files:
        result = check_file_exists(str(base_path / filepath), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # Analytics files
    print("📊 Analytics Files:")
    print("-" * 70)
    analytics_files = [
        ("analytics/dashboard_data.py", "Dashboard Generator"),
        ("analytics/simple_dashboard.html", "Dashboard UI"),
    ]
    
    for filepath, desc in analytics_files:
        result = check_file_exists(str(base_path / filepath), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # Directories
    print("📂 Key Directories:")
    print("-" * 70)
    directories = [
        ("api", "API Directory"),
        ("saas_landing", "SaaS Landing Directory"),
        ("analytics", "Analytics Directory"),
        ("scripts", "Scripts Directory"),
        ("templates", "Templates Directory"),
        ("integrations", "Integrations Directory"),
    ]
    
    for dirpath, desc in directories:
        result = check_directory_exists(str(base_path / dirpath), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # JSON files
    print("📄 Data Files:")
    print("-" * 70)
    json_files = [
        ("PROGRESS_STATUS.json", "Progress Status"),
        ("ai_memory.json", "AI Memory"),
    ]
    
    for filepath, desc in json_files:
        result = check_json_valid(str(base_path / filepath), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # Documentation
    print("📚 Documentation Files:")
    print("-" * 70)
    doc_files = [
        ("README.md", "Main README"),
        ("QUICK_START.md", "Quick Start Guide"),
        ("PROJECT_MAP.md", "Project Map"),
        ("CONTRIBUTING.md", "Contributing Guide"),
        ("CHANGELOG.md", "Changelog"),
        ("DEPLOYMENT_GUIDE.md", "Deployment Guide"),
    ]
    
    for filepath, desc in doc_files:
        result = check_file_exists(str(base_path / filepath), desc)
        checks.append(result)
        print(f"   {result[1]}")
    
    print()
    
    # Python imports (basic)
    print("🐍 Python Imports:")
    print("-" * 70)
    try:
        # Try importing key modules
        sys.path.insert(0, str(base_path))
        import ai_decision_engine
        checks.append((True, "✅ Decision Engine import"))
        print("   ✅ Decision Engine import")
        
        import income_strategies
        checks.append((True, "✅ Income Strategies import"))
        print("   ✅ Income Strategies import")
    except Exception as e:
        checks.append((False, f"❌ Import error: {e}"))
        print(f"   ❌ Import error: {e}")
    
    print()
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for success, _ in checks if success)
    total = len(checks)
    
    print(f"Passed: {passed}/{total} checks")
    print()
    
    if passed == total:
        print("🎉 All checks passed! System is ready.")
        return 0
    else:
        failed = [desc for success, desc in checks if not success]
        print(f"⚠️  {total - passed} check(s) failed:")
        for desc in failed:
            print(f"   {desc}")
        return 1

if __name__ == "__main__":
    exit(main())

