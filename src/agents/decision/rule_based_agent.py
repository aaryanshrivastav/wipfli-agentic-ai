"""Rule-Based Supply Chain Agent

Deterministic rule-based decision engine for supply chain actions.

Uses hardcoded business rules to make decisions based on:
- Inventory risk levels
- Supplier risk levels
- Days to stockout thresholds
- Historical patterns

This is the baseline agent implementation.
"""

from typing import Dict, Any
from .base_agent import BaseSupplyChainAgent


class RuleBasedAgent(BaseSupplyChainAgent):
    """Rule-based supply chain decision agent.
    
    Makes decisions using deterministic if-then rules based on
    inventory risk, supplier risk, and stockout projections.
    """
    
    def __init__(self):
        """Initialize the rule-based agent."""
        self.name = "rule_based_agent"
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a supply chain decision using business rules.
        
        Decision Rules (evaluated in order):
        1. If stockout projected within 7 days → EXPEDITE_PO (CRITICAL)
        2. If supplier risk is HIGH/CRITICAL → SUPPLIER_ALERT (HIGH)
        3. If inventory risk is HIGH/CRITICAL → REORDER (HIGH)
        4. Otherwise → NO_ACTION (LOW)
        
        Args:
            context: Dictionary with inventory_risk, supplier_risk, etc.
            
        Returns:
            Decision dictionary with action, priority, confidence, reasoning
        """
        inventory = context.get("inventory_risk", {})
        supplier = context.get("supplier_risk", {})
        
        # Rule 1: Critical stockout risk
        days_to_stockout = inventory.get("projected_days_to_stockout")
        if days_to_stockout is not None and days_to_stockout < 7:
            return {
                "action": "EXPEDITE_PO",
                "priority": "CRITICAL",
                "confidence": 0.95,
                "reasoning": (
                    f"Projected stockout within {days_to_stockout} days. "
                    "Immediate action required to prevent stockout."
                )
            }
        
        # Rule 2: Supplier risk
        supplier_risk_level = supplier.get("risk_level")
        if supplier_risk_level in ["HIGH", "CRITICAL"]:
            return {
                "action": "SUPPLIER_ALERT",
                "priority": "HIGH",
                "confidence": 0.90,
                "reasoning": (
                    f"Supplier risk level is {supplier_risk_level}. "
                    "Monitor supplier performance and consider alternatives."
                )
            }
        
        # Rule 3: Inventory risk
        inventory_risk_level = inventory.get("risk_level")
        if inventory_risk_level in ["HIGH", "CRITICAL"]:
            return {
                "action": "REORDER",
                "priority": "HIGH",
                "confidence": 0.88,
                "reasoning": (
                    f"Inventory risk level is {inventory_risk_level}. "
                    "Reorder needed to maintain safety stock."
                )
            }
        
        # Rule 4: No action needed
        return {
            "action": "NO_ACTION",
            "priority": "LOW",
            "confidence": 0.99,
            "reasoning": (
                "Inventory levels healthy. "
                "Supplier performance within acceptable range. "
                "No immediate action required."
            )
        }
    
    def get_name(self) -> str:
        """Return agent name."""
        return self.name
