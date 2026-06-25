"""Base Supply Chain Agent

Abstract base class defining the interface for all supply chain agent implementations.

This follows the Strategy Pattern, allowing different decision engines
(rule-based, LLM-based, hybrid) to be swapped without changing orchestration logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSupplyChainAgent(ABC):
    """Abstract base class for supply chain decision agents.
    
    All agent implementations must inherit from this class and implement
    the decide() method.
    """
    
    @abstractmethod
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a supply chain decision based on context.
        
        Args:
            context: Dictionary containing:
                - inventory_risk: Inventory risk data
                - supplier_risk: Supplier risk data
                - forecast: Demand forecast data
                - recommendation: Previous recommendation (if any)
                - purchase_orders: Open purchase orders
                
        Returns:
            Dictionary containing:
                - action: Action to take (REORDER, EXPEDITE_PO, SUPPLIER_ALERT, NO_ACTION)
                - priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
                - confidence: Confidence score (0.0 to 1.0)
                - reasoning: Explanation of the decision
                
        Example:
            {
                "action": "EXPEDITE_PO",
                "priority": "CRITICAL",
                "confidence": 0.95,
                "reasoning": "Projected stockout within 7 days."
            }
        """
        pass
    
    def get_name(self) -> str:
        """Return the name of this agent implementation.
        
        Returns:
            Agent name (e.g., "rule_based", "llama_3_1")
        """
        return self.__class__.__name__
