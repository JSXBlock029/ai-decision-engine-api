"""
One-Click Deployment Script
Simplified deployment with minimal configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_and_install_dependencies():
    """Check and install required dependencies"""
    print("Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies installed")
        return True
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "api/requirements.txt"])
        print("✅ Dependencies installed")
        return True

def deploy():
    """One-click deployment"""
    project_root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("ONE-CLICK DEPLOYMENT")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Start server
    print("Starting API server...")
    print("Server will run on: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        os.chdir(project_root)
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    deploy()

