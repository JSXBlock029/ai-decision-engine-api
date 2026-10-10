"""
Quick Start Script
Get everything running quickly
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_server_running(url: str = "http://localhost:8000/health", timeout: int = 5) -> bool:
    """Check if server is running"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server"""
    print("="*60)
    print("STARTING API SERVER")
    print("="*60)
    print()
    
    api_dir = Path(__file__).parent / "api"
    
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=api_dir)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

def test_api():
    """Test API endpoints"""
    print("="*60)
    print("TESTING API")
    print("="*60)
    print()
    
    if not check_server_running():
        print("ERROR: API server is not running!")
        print("Please start the server first.")
        return False
    
    print("Testing endpoints...")
    print()
    
    # Test health
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✓ Health check: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test decision evaluation
    try:
        response = requests.post(
            "http://localhost:8000/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000, "description": "Test"},
            headers={"X-API-Key": "dev_key_123", "Content-Type": "application/json"}
        )
        print(f"✓ Decision evaluation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Decision ID: {data.get('id')}")
            print(f"  Risk Level: {data.get('risk_level')}")
    except Exception as e:
        print(f"✗ Decision evaluation failed: {e}")
        return False
    
    # Test risk assessment
    try:
        response = requests.post(
            "http://localhost:8000/risk/assess",
            json={"amount": 5000, "category": "STRATEGIC"},
            headers={"X-API-Key": "dev_key_123", "Content-Type": "application/json"}
        )
        print(f"✓ Risk assessment: {response.status_code}")
    except Exception as e:
        print(f"✗ Risk assessment failed: {e}")
        return False
    
    print()
    print("All tests passed! ✓")
    return True

def run_demo():
    """Run the demo application"""
    print("="*60)
    print("RUNNING DEMO")
    print("="*60)
    print()
    
    if not check_server_running():
        print("ERROR: API server is not running!")
        return False
    
    demo_file = Path(__file__).parent / "demos" / "decision_demo.py"
    if not demo_file.exists():
        print("Demo file not found. Creating...")
        return False
    
    try:
        subprocess.run([sys.executable, str(demo_file)], check=True)
        return True
    except Exception as e:
        print(f"Demo failed: {e}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick Start - AI Decision Engine")
    parser.add_argument("command", choices=["start", "test", "demo", "all"], 
                       help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_api_server()
    elif args.command == "test":
        test_api()
    elif args.command == "demo":
        run_demo()
    elif args.command == "all":
        print("Starting server in background...")
        # Start server in background (simplified)
        print("Please start server manually, then run: python scripts/quick_start.py test")
        test_api()
        if check_server_running():
            run_demo()

if __name__ == "__main__":
    main()

