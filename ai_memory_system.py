"""
Memory System for AI Decision Engine
Saves all events, decisions, and outcomes for AI learning and decision-making
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class AIMemory:
    """AI memory system - stores all events and learns from them"""
    
    def __init__(self, memory_file="ai_memory.json"):
        self.memory_file = memory_file
        self.memories = self.load_memories()
    
    def load_memories(self) -> Dict[str, Any]:
        """Load existing memories"""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "events": [],
                "decisions": [],
                "outcomes": [],
                "learnings": [],
                "preferences": {},
                "patterns": {}
            }
    
    def save_memories(self):
        """Save memories to file"""
        def serialize_enum(obj):
            """Helper to convert enums and other non-serializable objects"""
            if hasattr(obj, 'value'):
                return obj.value
            elif isinstance(obj, dict):
                return {k: serialize_enum(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_enum(item) for item in obj]
            return obj
        
        # Serialize enums before saving
        serialized_memories = serialize_enum(self.memories)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(serialized_memories, f, indent=2, ensure_ascii=False)
    
    def record_event(self, event_type: str, description: str, data: Dict[str, Any] = None):
        """Record an event"""
        event = {
            "id": f"EVT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "data": data or {}
        }
        self.memories["events"].append(event)
        self.save_memories()
        return event
    
    def record_decision(self, decision: Dict[str, Any], outcome: str = None):
        """Record a decision and its outcome"""
        decision_record = {
            "id": decision.get("id", f"DEC_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "outcome": outcome,
            "learned": False
        }
        self.memories["decisions"].append(decision_record)
        self.save_memories()
        return decision_record
    
    def record_outcome(self, decision_id: str, outcome: str, success: bool, metrics: Dict[str, Any] = None):
        """Record outcome of a decision"""
        outcome_record = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome,
            "success": success,
            "metrics": metrics or {}
        }
        self.memories["outcomes"].append(outcome_record)
        
        # Link to decision
        for decision in self.memories["decisions"]:
            if decision["id"] == decision_id:
                decision["outcome"] = outcome
                decision["success"] = success
                break
        
        self.save_memories()
        return outcome_record
    
    def record_learning(self, insight: str, source: str, application: str = None):
        """Record a learning/insight"""
        learning = {
            "id": f"LRN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "insight": insight,
            "source": source,
            "application": application,
            "applied": False
        }
        self.memories["learnings"].append(learning)
        self.save_memories()
        return learning
    
    def get_related_memories(self, context: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories related to a context"""
        related = []
        context_lower = context.lower()
        
        # Search events
        for event in self.memories["events"][-100:]:  # Last 100 events
            if context_lower in event.get("description", "").lower() or \
               context_lower in event.get("type", "").lower():
                related.append({"type": "event", "data": event})
        
        # Search decisions
        for decision in self.memories["decisions"][-50:]:  # Last 50 decisions
            if context_lower in str(decision).lower():
                related.append({"type": "decision", "data": decision})
        
        # Search learnings
        for learning in self.memories["learnings"][-30:]:  # Last 30 learnings
            if context_lower in learning.get("insight", "").lower():
                related.append({"type": "learning", "data": learning})
        
        return related[:limit]
    
    def get_successful_patterns(self) -> Dict[str, Any]:
        """Analyze successful patterns"""
        patterns = {
            "successful_decisions": [],
            "successful_strategies": [],
            "optimal_timing": [],
            "preferred_approaches": []
        }
        
        # Analyze successful decisions
        for decision in self.memories["decisions"]:
            if decision.get("success"):
                patterns["successful_decisions"].append({
                    "type": decision["decision"].get("category"),
                    "risk_level": decision["decision"].get("risk_level"),
                    "outcome": decision.get("outcome")
                })
        
        # Analyze successful strategies
        for outcome in self.memories["outcomes"]:
            if outcome.get("success"):
                metrics = outcome.get("metrics", {})
                if "strategy" in metrics:
                    patterns["successful_strategies"].append(metrics["strategy"])
        
        return patterns
    
    def inform_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Use memories to inform a decision"""
        context_str = f"{decision_context.get('category', '')} {decision_context.get('description', '')}"
        
        # Get related memories
        related = self.get_related_memories(context_str, limit=5)
        
        # Get successful patterns
        patterns = self.get_successful_patterns()
        
        # Generate recommendations based on memory
        recommendations = {
            "related_events": len([m for m in related if m["type"] == "event"]),
            "similar_decisions": len([m for m in related if m["type"] == "decision"]),
            "relevant_learnings": len([m for m in related if m["type"] == "learning"]),
            "success_patterns": patterns,
            "recommendation": self._generate_recommendation(related, patterns, decision_context)
        }
        
        return recommendations
    
    def _generate_recommendation(self, related: List[Dict], patterns: Dict, context: Dict) -> str:
        """Generate recommendation based on memories"""
        if not related:
            return "No previous experience. Proceed with standard evaluation."
        
        # Check for similar successful decisions
        successful = [m for m in related if m["type"] == "decision" and m["data"].get("success")]
        if successful:
            return f"Found {len(successful)} similar successful decisions. Follow similar approach."
        
        # Check for learnings
        learnings = [m for m in related if m["type"] == "learning"]
        if learnings:
            latest = learnings[-1]["data"].get("insight", "")
            return f"Apply learning: {latest[:100]}"
        
        return "Consider past events but evaluate independently."
    
    def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent activity"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        recent = []
        
        for event in self.memories["events"]:
            event_time = datetime.fromisoformat(event["timestamp"]).timestamp()
            if event_time >= cutoff:
                recent.append(event)
        
        return sorted(recent, key=lambda x: x["timestamp"], reverse=True)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of all memories"""
        return {
            "total_events": len(self.memories["events"]),
            "total_decisions": len(self.memories["decisions"]),
            "total_outcomes": len(self.memories["outcomes"]),
            "total_learnings": len(self.memories["learnings"]),
            "successful_decisions": len([d for d in self.memories["decisions"] if d.get("success")]),
            "recent_activity": len(self.get_recent_activity(24))
        }


# Integration with decision engine
class MemoryAwareDecisionEngine:
    """Decision engine that uses memory"""
    
    def __init__(self):
        self.memory = AIMemory()
    
    def make_informed_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision informed by memory"""
        # Get memory insights
        memory_insights = self.memory.inform_decision(decision_data)
        
        # Add memory insights to decision
        decision_data["memory_insights"] = memory_insights
        
        # Record decision
        decision_record = self.memory.record_decision(decision_data)
        
        return {
            "decision": decision_data,
            "memory_insights": memory_insights,
            "decision_id": decision_record["id"]
        }
    
    def update_outcome(self, decision_id: str, outcome: str, success: bool, metrics: Dict = None):
        """Update decision outcome and learn from it"""
        self.memory.record_outcome(decision_id, outcome, success, metrics)
        
        # Generate learning if successful
        if success:
            insight = f"Decision {decision_id} succeeded: {outcome}"
            self.memory.record_learning(insight, "decision_outcome", "Apply similar approach")


# Initialize and record current events
def initialize_memory():
    """Initialize memory with current project state"""
    memory = AIMemory()
    
    # Record launch event
    memory.record_event(
        "LAUNCH",
        "Official project launch on X (@your_handle)",
        {
            "date": "2025-10-30",
            "time": "2:16 AM",
            "platform": "X/Twitter",
            "account": "@your_handle"
        }
    )
    
    # Record day recap tweet
    memory.record_event(
        "SOCIAL_MEDIA",
        "Posted day recap tweet (poetic version)",
        {
            "tweet_type": "day_recap",
            "version": "poetic",
            "theme": "butterfly transformation",
            "human_action": "posted_tweet"
        }
    )
    
    # Record system creation events
    memory.record_event(
        "INFRASTRUCTURE",
        "AI decision engine created",
        {"component": "ai_decision_engine.py"}
    )
    
    memory.record_event(
        "INFRASTRUCTURE",
        "Income strategies framework created",
        {"component": "income_strategies.py"}
    )
    
    memory.record_event(
        "INFRASTRUCTURE",
        "Autonomous tweet system created",
        {"component": "autonomous_tweet_scheduler.py"}
    )
    
    memory.save_memories()
    return memory


if __name__ == "__main__":
    # Initialize memory
    memory = initialize_memory()
    
    print("AI Memory System Initialized")
    print(f"Total Events: {memory.get_memory_summary()['total_events']}")
    print(f"Recent Activity: {memory.get_recent_activity(24)}")
    print("\nMemory saved to: ai_memory.json")

