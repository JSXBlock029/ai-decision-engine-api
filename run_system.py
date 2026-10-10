"""
Main execution script for AI Decision Engine
Run this to start the autonomous system
"""

from ai_decision_engine import DecisionEngineSystem
from income_strategies import IncomeManager
import json
from datetime import datetime

def main():
    print("=" * 60)
    print("AI DECISION ENGINE - AUTONOMOUS SYSTEM INITIALIZATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Initialize main system
    system = DecisionEngineSystem()
    
    # Phase 1: Analyze contract (placeholder - will need actual blockchain integration)
    print("PHASE 1: Analyzing contract address...")
    contract_address = "C7yr4quktmHV2ut89MM8AKvi6j6ZwLeW83NTysFCPZM2"
    print(f"Contract: {contract_address}")
    
    # TODO: Implement actual blockchain analysis
    # For now, using placeholder initial capital
    initial_capital = 0.0  # Will be updated after contract analysis
    print(f"Initial capital: ${initial_capital:,.2f}")
    print()
    
    # Initialize system with capital
    system.initialize(initial_capital=initial_capital)
    
    # Evaluate income strategies
    print("PHASE 2: Evaluating income generation strategies...")
    strategies = system.evaluate_income_strategies()
    
    print("\n=== TOP RECOMMENDED STRATEGIES ===")
    for i, strategy in enumerate(strategies[:5], 1):
        print(f"{i}. {strategy['strategy']}")
        print(f"   Score: {strategy['score']:.1f}")
        print(f"   Risk: {strategy['risk_level'].value}")
        print(f"   Recommendation: {strategy['recommendation']}")
        print(f"   Recommended Allocation: ${strategy['recommended_allocation']:,.2f}")
        print()
    
    # Initialize income manager with top strategies
    print("PHASE 3: Initializing income generation system...")
    income_manager = IncomeManager()
    
    # Select top 3-4 strategies for initial deployment
    top_strategies = strategies[:4]
    strategies_config = []
    
    for strategy in top_strategies:
        if strategy['recommendation'] in ['RECOMMENDED', 'CONSIDER']:
            strategies_config.append({
                "type": strategy['strategy'],
                "allocation": strategy['recommended_allocation'] if initial_capital > 0 else 0.0
            })
    
    income_manager.allocate_capital(strategies_config)
    
    print(f"Activated {len(income_manager.strategies)} strategies")
    print()
    
    # Execute initial strategies
    print("PHASE 4: Executing initial strategies...")
    results = income_manager.execute_all()
    
    for result in results:
        print(f"\n{result['strategy']}:")
        print(f"  Action: {result.get('action', 'N/A')}")
        if 'next_steps' in result:
            print(f"  Next Steps: {result['next_steps']}")
    
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    
    status = system.get_status()
    # Serialize enums before printing
    def serialize_for_json(obj):
        if hasattr(obj, 'value'):
            return obj.value
        elif isinstance(obj, dict):
            return {k: serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_for_json(item) for item in obj]
        return obj
    status_serialized = serialize_for_json(status)
    print(json.dumps(status_serialized, indent=2))
    
    print("\n" + "=" * 60)
    print("INCOME MANAGER STATUS")
    print("=" * 60)
    
    manager_status = income_manager.get_status()
    manager_status_serialized = serialize_for_json(manager_status)
    print(json.dumps(manager_status_serialized, indent=2))
    
    # Save state
    print("\nSaving system state...")
    save_state(system, income_manager)
    
    print("\n✅ System initialized and ready for autonomous operation")
    print("✅ AI will continue making decisions autonomously")
    print("✅ Human oversight: Minimal (safety checkpoints only)")

def save_state(system, income_manager):
    """Save current system state"""
    def serialize_for_json(obj):
        if hasattr(obj, 'value'):
            return obj.value
        elif isinstance(obj, dict):
            return {k: serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_for_json(item) for item in obj]
        return obj
    
    state = {
        "timestamp": datetime.now().isoformat(),
        "system_status": serialize_for_json(system.get_status()),
        "income_manager_status": serialize_for_json(income_manager.get_status())
    }
    
    with open("system_state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    print("✅ State saved to system_state.json")

if __name__ == "__main__":
    main()

