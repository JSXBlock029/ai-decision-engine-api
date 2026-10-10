"""
Production API Key Generator
Generate production-ready API keys
"""

import json
from pathlib import Path
from datetime import datetime
import secrets
import string

class ProductionKeyGenerator:
    """Generate production API keys"""
    
    def __init__(self):
        self.keys_file = "deployment/production_keys.json"
        self.keys_dir = Path("deployment")
        self.keys_dir.mkdir(exist_ok=True)
    
    def generate_key(self, length: int = 32) -> str:
        """Generate secure API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_production_keys(self):
        """Create production API keys"""
        print("="*60)
        print("GENERATING PRODUCTION API KEYS")
        print("="*60)
        print()
        
        keys = {
            "generated_at": datetime.now().isoformat(),
            "keys": {
                "free_tier": {
                    "key": f"prod_free_{self.generate_key(24)}",
                    "tier": "free",
                    "limit": 100,
                    "created": datetime.now().isoformat(),
                    "note": "Free tier - 100 requests/month"
                },
                "pro_tier": {
                    "key": f"prod_pro_{self.generate_key(24)}",
                    "tier": "pro",
                    "limit": 10000,
                    "created": datetime.now().isoformat(),
                    "note": "Pro tier - 10,000 requests/month"
                },
                "enterprise_tier": {
                    "key": f"prod_ent_{self.generate_key(24)}",
                    "tier": "enterprise",
                    "limit": 1000000,
                    "created": datetime.now().isoformat(),
                    "note": "Enterprise tier - 1,000,000 requests/month"
                }
            },
            "security_note": "These are example keys. Generate new ones for production!"
        }
        
        # Save keys
        with open(self.keys_file, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2)
        
        print("Production keys generated!")
        print(f"Saved to: {self.keys_file}")
        print()
        print("IMPORTANT: These are example keys.")
        print("Generate new secure keys for actual production use!")
        print()
        print("Keys generated:")
        for tier, key_info in keys["keys"].items():
            print(f"  {tier}: {key_info['key']}")
        
        return keys

def main():
    """Generate production keys"""
    generator = ProductionKeyGenerator()
    generator.create_production_keys()

if __name__ == "__main__":
    main()

