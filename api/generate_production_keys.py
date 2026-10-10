"""
Production Key Generator
Generates production-ready API keys for distribution
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_key_manager import api_key_manager
from datetime import datetime
import json

def generate_production_keys():
    """Generate a set of production keys for all tiers"""
    
    print("=" * 60)
    print("PRODUCTION API KEY GENERATOR")
    print("=" * 60)
    print()
    print("This will generate production-ready API keys.")
    print("Keys will be saved to api_keys.json")
    print()
    
    keys_generated = {}
    
    # Generate keys for each tier
    tiers = [
        ("free", "Free Tier - 100 requests/month"),
        ("pro", "Pro Tier - 10,000 requests/month"),
        ("enterprise", "Enterprise Tier - 1,000,000 requests/month")
    ]
    
    for tier, description in tiers:
        print(f"Generating {tier} tier key...")
        key = api_key_manager.generate_api_key(tier=tier, prefix="prod")
        keys_generated[tier] = {
            "key": key,
            "tier": tier,
            "description": description,
            "generated_at": datetime.now().isoformat()
        }
        print(f"  [OK] Generated: {key[:30]}...")
        print()
    
    # Save to file
    output_file = "production_keys_generated.json"
    with open(output_file, "w") as f:
        json.dump(keys_generated, f, indent=2)
    
    print("=" * 60)
    print("KEYS GENERATED SUCCESSFULLY")
    print("=" * 60)
    print()
    print(f"Keys saved to: {output_file}")
    print()
    print("IMPORTANT:")
    print("1. Store these keys securely")
    print("2. Do NOT commit to version control")
    print("3. Distribute to users via secure channels")
    print("4. Add api_keys.json to .gitignore")
    print()
    
    # Display keys (for easy copy)
    print("Generated Keys:")
    print("-" * 60)
    for tier, info in keys_generated.items():
        print(f"{tier.upper()}: {info['key']}")
    print()
    
    return keys_generated

if __name__ == "__main__":
    generate_production_keys()

