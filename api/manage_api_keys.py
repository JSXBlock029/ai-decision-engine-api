"""
API Key Management CLI
Command-line tool for managing API keys
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_key_manager import api_key_manager

def print_usage():
    """Print usage information"""
    print("=" * 60)
    print("API KEY MANAGEMENT CLI")
    print("=" * 60)
    print()
    print("Usage:")
    print("  python manage_api_keys.py generate [tier] [prefix]")
    print("    Generate a new API key")
    print("    tier: free, dev, pro, enterprise (default: free)")
    print("    prefix: Key prefix (default: key)")
    print()
    print("  python manage_api_keys.py list")
    print("    List all API keys")
    print()
    print("  python manage_api_keys.py deactivate <api_key>")
    print("    Deactivate an API key")
    print()
    print("  python manage_api_keys.py info <api_key>")
    print("    Get information about an API key")
    print()
    print("=" * 60)

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "generate":
        tier = sys.argv[2] if len(sys.argv) > 2 else "free"
        prefix = sys.argv[3] if len(sys.argv) > 3 else "key"
        
        api_key = api_key_manager.generate_api_key(tier=tier, prefix=prefix)
        print(f"[OK] Generated new API key:")
        print(f"   Key: {api_key}")
        print(f"   Tier: {tier}")
        print(f"   Requests/month: {api_key_manager._get_tier_limit(tier)}")
        print()
        print("[WARNING] Save this key securely - it won't be shown again!")
        
    elif command == "list":
        keys = api_key_manager.list_keys()
        print(f"Total API keys: {len(keys)}")
        print()
        for key, info in keys.items():
            status = "[ACTIVE]" if info.get("active") else "[INACTIVE]"
            print(f"{status} {key[:20]}...")
            print(f"   Tier: {info.get('tier')}")
            print(f"   Requests/month: {info.get('requests_per_month')}")
            print(f"   Created: {info.get('created_at')}")
            print()
    
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("[ERROR] API key required")
            print("Usage: python manage_api_keys.py deactivate <api_key>")
            return
        
        api_key = sys.argv[2]
        if api_key_manager.deactivate_key(api_key):
            print(f"[OK] API key deactivated: {api_key[:20]}...")
        else:
            print(f"[ERROR] API key not found: {api_key[:20]}...")
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("[ERROR] API key required")
            print("Usage: python manage_api_keys.py info <api_key>")
            return
        
        api_key = sys.argv[2]
        info = api_key_manager.get_key_info(api_key)
        if info:
            print(f"API Key: {api_key[:20]}...")
            print(f"Tier: {info.get('tier')}")
            print(f"Requests/month: {info.get('requests_per_month')}")
            print(f"Active: {info.get('active')}")
            print(f"Created: {info.get('created_at')}")
        else:
            print(f"[ERROR] API key not found: {api_key[:20]}...")
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main()

