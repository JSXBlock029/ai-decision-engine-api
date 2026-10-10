"""
Automated Deployment Script
Handles deployment to various platforms with minimal configuration
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class DeploymentManager:
    """Manage automated deployments"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        config_file = self.project_root / "deployment_config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        return {
            "platform": None,
            "api_url": None,
            "landing_url": None,
            "waitlist_url": None
        }
    
    def _save_config(self, config: Dict[str, Any]):
        """Save deployment configuration"""
        config_file = self.project_root / "deployment_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites are met"""
        checks = {
            "python": False,
            "git": False,
            "api_files": False,
            "landing_files": False
        }
        
        # Check Python
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True
            )
            checks["python"] = result.returncode == 0
        except:
            pass
        
        # Check Git
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            checks["git"] = result.returncode == 0
        except:
            pass
        
        # Check API files
        api_main = self.project_root / "api" / "main.py"
        checks["api_files"] = api_main.exists()
        
        # Check landing files
        landing_index = self.project_root / "saas_landing" / "index.html"
        checks["landing_files"] = landing_index.exists()
        
        return checks
    
    def run_tests(self) -> bool:
        """Run tests before deployment"""
        print("Running pre-deployment tests...")
        
        try:
            # Test API imports
            result = subprocess.run(
                [sys.executable, "-c", "from api.main import app; print('OK')"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ API import test failed")
                return False
            
            print("✅ API import test passed")
            return True
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    
    def deploy_railway(self) -> bool:
        """Deploy to Railway"""
        print("Deploying to Railway...")
        
        # Check for Railway CLI
        try:
            result = subprocess.run(
                ["railway", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("⚠️  Railway CLI not found. Install: npm i -g @railway/cli")
                return False
        except:
            print("⚠️  Railway CLI not found. Install: npm i -g @railway/cli")
            return False
        
        # Deploy
        try:
            subprocess.run(
                ["railway", "up"],
                cwd=self.project_root,
                check=True
            )
            print("✅ Deployed to Railway")
            return True
        except Exception as e:
            print(f"❌ Railway deployment failed: {e}")
            return False
    
    def deploy_render(self) -> bool:
        """Deploy to Render"""
        print("Deploying to Render...")
        print("⚠️  Render deployment requires manual setup:")
        print("   1. Go to render.com")
        print("   2. Create new Web Service")
        print("   3. Connect GitHub repository")
        print("   4. Set build command: pip install -r api/requirements.txt")
        print("   5. Set start command: uvicorn api.main:app --host 0.0.0.0 --port $PORT")
        return False
    
    def deploy_heroku(self) -> bool:
        """Deploy to Heroku"""
        print("Deploying to Heroku...")
        
        # Check for Heroku CLI
        try:
            result = subprocess.run(
                ["heroku", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("⚠️  Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli")
                return False
        except:
            print("⚠️  Heroku CLI not found")
            return False
        
        # Check if app exists
        app_name = os.getenv("HEROKU_APP_NAME", "ai-decision-engine-api")
        
        try:
            # Create app if doesn't exist
            subprocess.run(
                ["heroku", "create", app_name],
                cwd=self.project_root,
                check=False
            )
            
            # Deploy
            subprocess.run(
                ["git", "push", "heroku", "main"],
                cwd=self.project_root,
                check=True
            )
            
            print(f"✅ Deployed to Heroku: https://{app_name}.herokuapp.com")
            return True
        except Exception as e:
            print(f"❌ Heroku deployment failed: {e}")
            return False
    
    def deploy_docker(self) -> bool:
        """Deploy using Docker"""
        print("Deploying with Docker...")
        
        # Check for Docker
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("⚠️  Docker not found")
                return False
        except:
            print("⚠️  Docker not found")
            return False
        
        # Build and run
        try:
            # Build image
            subprocess.run(
                ["docker", "build", "-t", "ai-decision-engine", "-f", "api/Dockerfile.prod", "."],
                cwd=self.project_root,
                check=True
            )
            
            print("✅ Docker image built")
            print("Run with: docker run -p 8000:8000 ai-decision-engine")
            return True
        except Exception as e:
            print(f"❌ Docker build failed: {e}")
            return False
    
    def deploy_local(self) -> bool:
        """Deploy locally for testing"""
        print("Starting local deployment...")
        
        try:
            # Start API server
            print("Starting API server on http://localhost:8000")
            subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd=self.project_root
            )
            
            print("✅ Local deployment started")
            print("   API: http://localhost:8000")
            print("   Docs: http://localhost:8000/docs")
            return True
        except Exception as e:
            print(f"❌ Local deployment failed: {e}")
            return False
    
    def create_deployment_package(self) -> bool:
        """Create deployment package"""
        print("Creating deployment package...")
        
        package_dir = self.project_root / "deploy_package"
        package_dir.mkdir(exist_ok=True)
        
        # Copy necessary files
        files_to_copy = [
            "api/main.py",
            "api/requirements.txt",
            "api/api_key_manager.py",
            "api/analytics.py",
            "api/analytics_middleware.py",
            "api/analytics_routes.py",
            "api/key_management_routes.py",
            "api/production_config.py",
            "api/utils.py",
            "ai_decision_engine.py",
            "ai_memory_system.py",
            "autonomy_tracker.py"
        ]
        
        for file_path in files_to_copy:
            src = self.project_root / file_path
            if src.exists():
                dst = package_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(src, dst)
        
        print(f"✅ Deployment package created in: {package_dir}")
        return True

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy AI Decision Engine API")
    parser.add_argument(
        "platform",
        choices=["railway", "render", "heroku", "docker", "local", "package"],
        help="Deployment platform"
    )
    parser.add_argument("--skip-tests", action="store_true", help="Skip pre-deployment tests")
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    print("=" * 60)
    print("AI DECISION ENGINE - AUTOMATED DEPLOYMENT")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    checks = manager.check_prerequisites()
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    if not all(checks.values()):
        print("\n⚠️  Some prerequisites missing. Deployment may fail.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            return
    
    # Run tests
    if not args.skip_tests:
        if not manager.run_tests():
            print("\n❌ Tests failed. Use --skip-tests to deploy anyway.")
            return
    
    # Deploy
    print(f"\nDeploying to {args.platform}...")
    success = False
    
    if args.platform == "railway":
        success = manager.deploy_railway()
    elif args.platform == "render":
        success = manager.deploy_render()
    elif args.platform == "heroku":
        success = manager.deploy_heroku()
    elif args.platform == "docker":
        success = manager.deploy_docker()
    elif args.platform == "local":
        success = manager.deploy_local()
    elif args.platform == "package":
        success = manager.create_deployment_package()
    
    if success:
        print("\n✅ Deployment completed successfully!")
    else:
        print("\n❌ Deployment failed. Check errors above.")

if __name__ == "__main__":
    main()

