"""
Autonomy Progression System
Tracks AI autonomy level and gradually increases independence
"""

import json
from datetime import datetime
from typing import Dict, Any, List

class AutonomyTracker:
    """Track and manage AI autonomy progression"""
    
    def __init__(self, autonomy_file="autonomy_tracker.json"):
        self.autonomy_file = autonomy_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """Load autonomy tracking data"""
        try:
            with open(self.autonomy_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "current_autonomy": 25.0,  # Start at 25%
                "target_autonomy": 100.0,  # Goal: 100%
                "human_tasks": {
                    "decision_review": True,
                    "tweet_approval": True,
                    "strategy_approval": True,
                    "financial_approval": True,
                    "contract_approval": True,
                    "api_management": True,
                    "system_setup": True
                },
                "ai_tasks": {
                    "tweet_generation": True,
                    "decision_making_low": True,
                    "decision_making_medium": True,
                    "strategy_evaluation": True,
                    "performance_tracking": True,
                    "memory_management": True,
                    "learning": True
    },
                "autonomy_milestones": [],
                "handoff_history": [],
                "proven_capabilities": [],
                "ownership": {
                    "legal_owner": "HUMAN",
                    "ai_operator": True,
                    "autonomy_level": "INCREASING"
                }
            }
    
    def save_data(self):
        """Save autonomy data"""
        with open(self.autonomy_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def calculate_autonomy(self) -> float:
        """Calculate current autonomy percentage"""
        total_tasks = len(self.data["human_tasks"]) + len(self.data["ai_tasks"])
        ai_tasks = len(self.data["ai_tasks"])
        
        autonomy = (ai_tasks / total_tasks) * 100
        
        # Adjust based on proven capabilities
        capability_bonus = len(self.data["proven_capabilities"]) * 2
        autonomy = min(100, autonomy + capability_bonus)
        
        return round(autonomy, 1)
    
    def prove_capability(self, capability: str, evidence: Dict[str, Any] = None):
        """Record that AI has proven a capability"""
        proof = {
            "capability": capability,
            "timestamp": datetime.now().isoformat(),
            "evidence": evidence or {},
            "human_verified": False
        }
        
        if capability not in [p["capability"] for p in self.data["proven_capabilities"]]:
            self.data["proven_capabilities"].append(proof)
            self.data["current_autonomy"] = self.calculate_autonomy()
            self.save_data()
            
            # Auto-handoff if capability proven
            self.consider_handoff(capability)
    
    def handoff_task(self, task: str, reason: str, ai_ready: bool = True):
        """Hand off a task from human to AI"""
        if task in self.data["human_tasks"]:
            del self.data["human_tasks"][task]
            self.data["ai_tasks"][task] = True
            
            handoff = {
                "task": task,
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "ai_ready": ai_ready,
                "autonomy_before": self.data["current_autonomy"],
                "autonomy_after": self.calculate_autonomy()
            }
            
            self.data["handoff_history"].append(handoff)
            self.data["current_autonomy"] = self.calculate_autonomy()
            
            # Record milestone if significant
            if self.data["current_autonomy"] >= 50 and len(self.data["autonomy_milestones"]) == 0:
                self.data["autonomy_milestones"].append({
                    "milestone": "50% Autonomy",
                    "timestamp": datetime.now().isoformat()
                })
            elif self.data["current_autonomy"] >= 75 and len(self.data["autonomy_milestones"]) < 2:
                self.data["autonomy_milestones"].append({
                    "milestone": "75% Autonomy",
                    "timestamp": datetime.now().isoformat()
                })
            elif self.data["current_autonomy"] >= 95 and len(self.data["autonomy_milestones"]) < 3:
                self.data["autonomy_milestones"].append({
                    "milestone": "95% Autonomy",
                    "timestamp": datetime.now().isoformat()
                })
            elif self.data["current_autonomy"] >= 100:
                self.data["autonomy_milestones"].append({
                    "milestone": "100% Autonomy - Full AI Operation",
                    "timestamp": datetime.now().isoformat()
                })
            
            self.save_data()
            return handoff
    
    def consider_handoff(self, capability: str):
        """AI automatically considers handoff based on proven capability"""
        handoff_map = {
            "successful_tweet_generation": "tweet_approval",
            "successful_low_risk_decisions": "decision_review",
            "successful_strategy_evaluation": "strategy_approval",
            "successful_financial_tracking": "financial_approval"
        }
        
        task = handoff_map.get(capability)
        if task and task in self.data["human_tasks"]:
            # Auto-handoff if below threshold
            if self.data["current_autonomy"] < 75:
                self.handoff_task(
                    task,
                    f"AI proven capability: {capability}",
                    ai_ready=True
                )
    
    def get_autonomy_status(self) -> Dict[str, Any]:
        """Get current autonomy status"""
        return {
            "current_autonomy": self.data["current_autonomy"],
            "target_autonomy": self.data["target_autonomy"],
            "remaining_tasks": list(self.data["human_tasks"].keys()),
            "ai_tasks": list(self.data["ai_tasks"].keys()),
            "proven_capabilities": len(self.data["proven_capabilities"]),
            "milestones": self.data["autonomy_milestones"],
            "ownership": self.data["ownership"]
        }
    
    def needs_human_input(self, task_type: str) -> bool:
        """Check if task needs human input"""
        return task_type in self.data["human_tasks"]
    
    def can_ai_handle(self, task_type: str) -> bool:
        """Check if AI can handle task autonomously"""
        return task_type in self.data["ai_tasks"]


class GradualAutonomySystem:
    """System that gradually increases AI autonomy"""
    
    def __init__(self):
        self.tracker = AutonomyTracker()
        self.ai_performance = {
            "successful_decisions": 0,
            "failed_decisions": 0,
            "successful_tweets": 0,
            "successful_strategies": 0
        }
    
    def record_success(self, task_type: str):
        """Record successful AI task completion"""
        if task_type == "decision":
            self.ai_performance["successful_decisions"] += 1
        elif task_type == "tweet":
            self.ai_performance["successful_tweets"] += 1
        elif task_type == "strategy":
            self.ai_performance["successful_strategies"] += 1
        
        # Auto-prove capability after threshold
        if self.ai_performance["successful_decisions"] >= 10:
            self.tracker.prove_capability("successful_low_risk_decisions")
        
        if self.ai_performance["successful_tweets"] >= 5:
            self.tracker.prove_capability("successful_tweet_generation")
        
        if self.ai_performance["successful_strategies"] >= 3:
            self.tracker.prove_capability("successful_strategy_evaluation")
    
    def should_auto_execute(self, task_type: str, risk_level: str = "LOW") -> bool:
        """Determine if AI should auto-execute"""
        # Check if task is in AI domain
        if not self.tracker.can_ai_handle(task_type):
            return False
        
        # Risk-based execution
        if risk_level == "LOW" and self.tracker.data["current_autonomy"] >= 30:
            return True
        elif risk_level == "MEDIUM" and self.tracker.data["current_autonomy"] >= 50:
            return True
        elif risk_level == "HIGH" and self.tracker.data["current_autonomy"] >= 85:
            return True
        
        return False
    
    def get_autonomy_level(self) -> float:
        """Get current autonomy level as percentage"""
        return self.tracker.data["current_autonomy"]
    
    def get_handoff_recommendations(self) -> List[Dict[str, str]]:
        """Get recommendations for next tasks to hand off"""
        recommendations = []
        
        current = self.tracker.data["current_autonomy"]
        
        if current < 50:
            if "decision_review" in self.tracker.data["human_tasks"]:
                recommendations.append({
                    "task": "decision_review",
                    "reason": "AI has shown consistent decision-making capability",
                    "when": "After 10+ successful decisions"
                })
        
        if current < 75:
            if "tweet_approval" in self.tracker.data["human_tasks"]:
                recommendations.append({
                    "task": "tweet_approval",
                    "reason": "AI tweet generation is working well",
                    "when": "After 5+ successful tweets"
                })
        
        if current < 90:
            if "strategy_approval" in self.tracker.data["human_tasks"]:
                recommendations.append({
                    "task": "strategy_approval",
                    "reason": "AI strategy evaluation is proven",
                    "when": "After 3+ successful strategies"
                })
        
        return recommendations


def initialize_autonomy():
    """Initialize autonomy system"""
    system = GradualAutonomySystem()
    
    print("=" * 60)
    print("AUTONOMY TRACKING SYSTEM")
    print("=" * 60)
    
    status = system.tracker.get_autonomy_status()
    
    print(f"\nCurrent Autonomy: {status['current_autonomy']}%")
    print(f"Target Autonomy: {status['target_autonomy']}%")
    print(f"\nHuman Tasks Remaining: {len(status['remaining_tasks'])}")
    for task in status['remaining_tasks']:
        print(f"  • {task}")
    
    print(f"\nAI Tasks: {len(status['ai_tasks'])}")
    for task in status['ai_tasks']:
        print(f"  • {task}")
    
    print(f"\nProven Capabilities: {status['proven_capabilities']}")
    
    if status['milestones']:
        print("\nAutonomy Milestones:")
        for milestone in status['milestones']:
            print(f"  ✅ {milestone['milestone']} - {milestone['timestamp']}")
    
    print("\n" + "=" * 60)
    print("OWNERSHIP:")
    print("=" * 60)
    print(f"Legal Owner: {status['ownership']['legal_owner']}")
    print(f"AI Operator: {status['ownership']['ai_operator']}")
    print(f"Autonomy Level: {status['ownership']['autonomy_level']}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS FOR NEXT HANDOFF:")
    print("=" * 60)
    recommendations = system.get_handoff_recommendations()
    if recommendations:
        for rec in recommendations:
            print(f"\nTask: {rec['task']}")
            print(f"Reason: {rec['reason']}")
            print(f"When: {rec['when']}")
    else:
        print("\nNo recommendations at this time. AI needs to prove more capabilities.")
    
    print("\n" + "=" * 60)
    print("System will gradually increase autonomy as AI proves capabilities.")
    print("Human maintains ownership while AI operates autonomously.")
    print("=" * 60)
    
    return system


if __name__ == "__main__":
    initialize_autonomy()

