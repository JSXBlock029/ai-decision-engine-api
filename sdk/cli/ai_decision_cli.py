"""
CLI Tool for Developers
Command-line interface for API operations
"""

import argparse
import sys
import json
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk" / "python"))

try:
    from ai_decision_engine import AIDecisionEngineClient
except ImportError:
    print("SDK not found. Using direct API calls.")
    AIDecisionEngineClient = None

def load_config():
    """Load configuration from file"""
    config_file = Path.home() / ".ai_decision_engine" / "config.json"
    if config_file.exists():
        with open(config_file, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to file"""
    config_file = Path.home() / ".ai_decision_engine" / "config.json"
    config_file.parent.mkdir(exist_ok=True)
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

def cmd_health(args):
    """Health check command"""
    if AIDecisionEngineClient:
        client = AIDecisionEngineClient(args.api_key, args.base_url)
        health = client.health_check()
        print(json.dumps(health, indent=2))
    else:
        import requests
        response = requests.get(f"{args.base_url}/health")
        print(json.dumps(response.json(), indent=2))

def cmd_evaluate(args):
    """Evaluate decision command"""
    if AIDecisionEngineClient:
        client = AIDecisionEngineClient(args.api_key, args.base_url)
        result = client.evaluate_decision(
            category=args.category,
            amount=args.amount,
            description=args.description
        )
        print(json.dumps(result, indent=2))
    else:
        import requests
        response = requests.post(
            f"{args.base_url}/decisions/evaluate",
            json={
                "category": args.category,
                "amount": args.amount,
                "description": args.description
            },
            headers={"X-API-Key": args.api_key, "Content-Type": "application/json"}
        )
        print(json.dumps(response.json(), indent=2))

def cmd_risk(args):
    """Risk assessment command"""
    if AIDecisionEngineClient:
        client = AIDecisionEngineClient(args.api_key, args.base_url)
        result = client.assess_risk(
            amount=args.amount,
            category=args.category,
            description=args.description
        )
        print(json.dumps(result, indent=2))
    else:
        import requests
        response = requests.post(
            f"{args.base_url}/risk/assess",
            json={
                "amount": args.amount,
                "category": args.category,
                "description": args.description
            },
            headers={"X-API-Key": args.api_key, "Content-Type": "application/json"}
        )
        print(json.dumps(response.json(), indent=2))

def cmd_autonomy(args):
    """Get autonomy level command"""
    if AIDecisionEngineClient:
        client = AIDecisionEngineClient(args.api_key, args.base_url)
        result = client.get_autonomy_level()
        print(json.dumps(result, indent=2))
    else:
        import requests
        response = requests.get(
            f"{args.base_url}/autonomy/level",
            headers={"X-API-Key": args.api_key}
        )
        print(json.dumps(response.json(), indent=2))

def cmd_config(args):
    """Configure CLI"""
    config = load_config()
    
    if args.api_key:
        config["api_key"] = args.api_key
    if args.base_url:
        config["base_url"] = args.base_url
    
    save_config(config)
    print("Configuration saved!")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Decision Engine CLI")
    
    # Global options
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--base-url", default="https://api.example.com", help="Base URL")
    
    # Load config
    config = load_config()
    if config.get("api_key"):
        parser.set_defaults(api_key=config["api_key"])
    if config.get("base_url"):
        parser.set_defaults(base_url=config["base_url"])
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check API health")
    health_parser.set_defaults(func=cmd_health)
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a decision")
    eval_parser.add_argument("category", help="Decision category")
    eval_parser.add_argument("--amount", type=float, default=0.0, help="Amount")
    eval_parser.add_argument("--description", default="", help="Description")
    eval_parser.set_defaults(func=cmd_evaluate)
    
    # Risk command
    risk_parser = subparsers.add_parser("risk", help="Assess risk")
    risk_parser.add_argument("amount", type=float, help="Amount")
    risk_parser.add_argument("--category", default="OPERATIONAL", help="Category")
    risk_parser.add_argument("--description", default="", help="Description")
    risk_parser.set_defaults(func=cmd_risk)
    
    # Autonomy command
    autonomy_parser = subparsers.add_parser("autonomy", help="Get autonomy level")
    autonomy_parser.set_defaults(func=cmd_autonomy)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure CLI")
    config_parser.add_argument("--api-key", help="Set API key")
    config_parser.add_argument("--base-url", help="Set base URL")
    config_parser.set_defaults(func=cmd_config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if not args.api_key and args.command != "config":
        print("Error: API key required. Use 'config --api-key <key>' or '--api-key <key>'")
        sys.exit(1)
    
    args.func(args)

if __name__ == "__main__":
    main()

