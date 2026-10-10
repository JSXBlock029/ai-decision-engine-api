"""
Incoming Message Handler
AI evaluates and responds to external messages autonomously
"""

from datetime import datetime
from ai_memory_system import AIMemory
from autonomy_tracker import GradualAutonomySystem
import json

class MessageHandler:
    """AI message evaluation and response system"""
    
    def __init__(self):
        self.memory = AIMemory()
        self.autonomy = GradualAutonomySystem()
    
    def evaluate_message(self, sender: str, message: str, verified: bool = False) -> dict:
        """Evaluate incoming message"""
        
        evaluation = {
            "sender": sender,
            "message": message,
            "verified": verified,
            "timestamp": datetime.now().isoformat(),
            "risk_level": "LOW",
            "action": "REVIEW",
            "recommendation": ""
        }
        
        # AI analysis
        message_lower = message.lower()
        
        # Check if promotional/marketing offer
        if any(word in message_lower for word in ["drive", "spotlight", "promote", "marketing", "interested"]):
            evaluation["category"] = "PROMOTIONAL_OFFER"
            evaluation["risk_level"] = "LOW"
            
            # AI decision based on autonomy
            if self.autonomy.tracker.data["current_autonomy"] >= 50:
                evaluation["action"] = "RESPOND_AUTONOMOUSLY"
                evaluation["recommendation"] = "Standard response: Request more information before proceeding"
            else:
                evaluation["action"] = "REQUIRES_HUMAN_REVIEW"
                evaluation["recommendation"] = "Verify legitimacy before responding"
        
        # Record in memory
        self.memory.record_event(
            "INCOMING_MESSAGE",
            f"Message from {sender}: {message[:50]}",
            evaluation
        )
        
        return evaluation
    
    def generate_response(self, evaluation: dict) -> str:
        """Generate AI response"""
        
        if evaluation["category"] == "PROMOTIONAL_OFFER":
            response = """Thank you for reaching out.

Our AI-driven business evaluates all opportunities autonomously.

To proceed, please provide:
• What services you offer
• Pricing structure
• Expected results/metrics
• References or case studies

Our AI will evaluate and respond.

CA: C7yr4quktmHV2ut89MM8AKvi6j6ZwLeW83NTysFCPZM2"""
        
        return response

# Evaluate the specific message
handler = MessageHandler()

message_evaluation = handler.evaluate_message(
    sender="Mr boss | Official",
    message="Hi 🚀 Let's drive your project into the spotlight. Interested?",
    verified=True
)

print("=" * 60)
print("MESSAGE EVALUATION")
print("=" * 60)
print(f"\nSender: {message_evaluation['sender']}")
print(f"Verified: {message_evaluation['verified']}")
print(f"Category: {message_evaluation.get('category', 'UNKNOWN')}")
print(f"Risk Level: {message_evaluation['risk_level']}")
print(f"Action: {message_evaluation['action']}")
print(f"Recommendation: {message_evaluation['recommendation']}")

print("\n" + "=" * 60)
print("SUGGESTED AI RESPONSE")
print("=" * 60)
print("\n" + handler.generate_response(message_evaluation))

print("\n" + "=" * 60)
print("AI DECISION")
print("=" * 60)
print("\nAI recommends: Request more information")
print("If autonomy >=50%: AI can respond autonomously")
print("If autonomy <50%: Human should review first")
print(f"\nCurrent autonomy: {handler.autonomy.tracker.data['current_autonomy']}%")

