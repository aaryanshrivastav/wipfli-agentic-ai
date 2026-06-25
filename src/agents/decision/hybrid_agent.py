"""Hybrid Supply Chain Agent

Combines Rule-Based and LLM-Based decision making for production use.

STRATEGY:
- Use deterministic rules for clear-cut cases (LOW complexity)
- Use LLM for ambiguous or high-impact cases (HIGH complexity)

This is the recommended production pattern:
- Fast and cost-effective for simple cases
- Nuanced reasoning for complex cases
- Reduces hallucination risk
- Lower API costs

Decision Flow:
    Rule Engine
         ↓
    Complexity Scoring
         ↓
    LOW score? → Rule Decision (fast path)
         ↓
    HIGH score? → LLM Decision (nuanced path)
         ↓
    Validate
         ↓
    Return

Usage:
    from decision.hybrid_agent import HybridAgent
    
    agent = HybridAgent()
    result = agent.decide(context)
    
    # Check decision details
    print(result['decision_engine'])       # 'rule' or 'llama'
    print(result['engine_status'])         # 'SUCCESS' or 'FAILED'
    print(result.get('fallback_reason'))   # If LLM failed
"""

from typing import Dict, Any
from .base_agent import BaseSupplyChainAgent
from .rule_based_agent import RuleBasedAgent
from .llama_agent import LlamaSupplyChainAgent


class HybridAgent(BaseSupplyChainAgent):
    """Hybrid agent using rules for simple cases, LLM for complex cases.
    
    This is the recommended production pattern:
    - Rules handle ~70-80% of cases (clear-cut LOW complexity)
    - LLM handles ~20-30% of cases (ambiguous HIGH complexity)
    - Best of both worlds: speed + nuance
    """
    
    def __init__(
        self,
        llm_temperature: float = 0.1,
        llm_max_tokens: int = 500,
        complexity_threshold: float = 3.0
    ):
        """Initialize hybrid agent with both rule and LLM engines.
        
        Args:
            llm_temperature: Temperature for LLM calls
            llm_max_tokens: Max tokens for LLM responses
            complexity_threshold: Complexity score threshold (>= threshold → LLM)
        """
        self.rule_agent = RuleBasedAgent()
        self.llama_agent = LlamaSupplyChainAgent(
            temperature=llm_temperature,
            max_tokens=llm_max_tokens
        )
        self.name = "hybrid_agent"
        self.complexity_threshold = complexity_threshold
        
        # Track which engine was used (for metrics)
        self.last_engine_used = None
        self.last_complexity_score = None
    
    def _compute_complexity_score(self, context: Dict[str, Any]) -> float:
        """Compute complexity score to route to appropriate engine.
        
        Uses a scoring function instead of binary rules.
        Higher score = more complex = route to LLM.
        
        Args:
            context: Decision context
            
        Returns:
            Complexity score (0-10+ range)
        """
        score = 0.0
        
        inventory = context.get("inventory_risk", {})
        supplier = context.get("supplier_risk", {})
        recommendation_history = context.get("recommendation_history", [])
        purchase_orders = context.get("purchase_orders", {})
        
        # +3 for imminent stockout (< 7 days)
        days_to_stockout = inventory.get("projected_days_to_stockout")
        if days_to_stockout is not None:
            if days_to_stockout < 7:
                score += 3.0
            elif days_to_stockout < 14:
                score += 1.5
        
        # +2 for CRITICAL inventory risk
        if inventory.get("risk_level") == "CRITICAL":
            score += 2.0
        elif inventory.get("risk_level") == "HIGH":
            score += 1.0
        
        # +2 for CRITICAL supplier risk
        if supplier.get("risk_level") == "CRITICAL":
            score += 2.0
        elif supplier.get("risk_level") == "HIGH":
            score += 1.0
        
        # +2 for repeated recommendations (not working)
        if len(recommendation_history) >= 3:
            # Check if last 3 recommendations were the same action
            recent_actions = [h.get('action') for h in recommendation_history[:3]]
            if len(set(recent_actions)) == 1:
                score += 2.0
        
        # +1.5 for conflicting signals (both risks high)
        inventory_risk_high = inventory.get("risk_level") in ["HIGH", "CRITICAL"]
        supplier_risk_high = supplier.get("risk_level") in ["HIGH", "CRITICAL"]
        if inventory_risk_high and supplier_risk_high:
            score += 1.5
        
        # +0.5 for multiple open purchase orders (coordination complexity)
        open_po_count = purchase_orders.get("open_po_count", 0)
        if open_po_count >= 3:
            score += 0.5
        
        # +1 for high forecast uncertainty (if available)
        forecast_uncertainty = context.get("forecast", {}).get("uncertainty", None)
        if forecast_uncertainty is not None and forecast_uncertainty > 0.3:
            score += 1.0
        
        return score
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision using hybrid approach.
        
        Args:
            context: Decision context
            
        Returns:
            Decision dictionary with action, priority, confidence, reasoning,
            plus metadata about which engine was used and why
        """
        # Compute complexity score
        complexity_score = self._compute_complexity_score(context)
        self.last_complexity_score = complexity_score
        
        if complexity_score < self.complexity_threshold:
            # Fast path: Use rules for simple cases
            self.last_engine_used = "rule"
            decision = self.rule_agent.decide(context)
            
            # Add metadata
            decision["decision_engine"] = "rule"
            decision["engine_status"] = "SUCCESS"
            decision["complexity_score"] = complexity_score
            decision["complexity_assessment"] = "SIMPLE"
            
            return decision
        
        else:
            # Complex path: Use LLM for nuanced cases
            self.last_engine_used = "llama"
            
            try:
                decision = self.llama_agent.decide(context)
                
                # Validate LLM decision
                if not self._validate_llm_decision(decision):
                    # Fallback to rules if LLM fails validation
                    rule_decision = self.rule_agent.decide(context)
                    
                    # Clear metadata: THIS IS A RULE FALLBACK, NOT AN LLM DECISION
                    rule_decision["decision_engine"] = "rule_fallback"
                    rule_decision["engine_status"] = "FAILED"
                    rule_decision["fallback_reason"] = "LLM decision failed validation"
                    rule_decision["complexity_score"] = complexity_score
                    rule_decision["complexity_assessment"] = "COMPLEX"
                    rule_decision["attempted_engine"] = "llama"
                    
                    return rule_decision
                else:
                    decision["decision_engine"] = "llama"
                    decision["engine_status"] = "SUCCESS"
                    decision["complexity_score"] = complexity_score
                    decision["complexity_assessment"] = "COMPLEX"
                    
                    return decision
                
            except Exception as e:
                # Fallback to rules if LLM fails
                rule_decision = self.rule_agent.decide(context)
                
                # Clear metadata: THIS IS A RULE FALLBACK, NOT AN LLM DECISION
                rule_decision["decision_engine"] = "rule_fallback"
                rule_decision["engine_status"] = "FAILED"
                rule_decision["fallback_reason"] = f"LLM error: {str(e)}"
                rule_decision["complexity_score"] = complexity_score
                rule_decision["complexity_assessment"] = "COMPLEX"
                rule_decision["attempted_engine"] = "llama"
                
                return rule_decision
    
    def _validate_llm_decision(self, decision: Dict[str, Any]) -> bool:
        """Validate LLM decision meets business constraints.
        
        Args:
            decision: LLM decision dictionary
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["action", "priority", "confidence", "reasoning"]
        for field in required_fields:
            if field not in decision:
                return False
        
        # Check action is valid
        valid_actions = ["EXPEDITE_PO", "REORDER", "SUPPLIER_ALERT", "NO_ACTION"]
        if decision["action"] not in valid_actions:
            return False
        
        # Check priority is valid
        valid_priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        if decision["priority"] not in valid_priorities:
            return False
        
        # Check confidence is in range
        try:
            conf = float(decision["confidence"])
            if conf < 0.0 or conf > 1.0:
                return False
        except (ValueError, TypeError):
            return False
        
        # Check reasoning is not empty
        if not decision["reasoning"] or len(decision["reasoning"]) < 10:
            return False
        
        return True
    
    def get_name(self) -> str:
        """Return agent name."""
        return self.name
    
    def get_last_engine_used(self) -> str:
        """Return which engine was used for the last decision.
        
        Returns:
            "rule", "llama", or "rule_fallback"
        """
        return self.last_engine_used
    
    def get_last_complexity_score(self) -> float:
        """Return the complexity score from the last decision.
        
        Returns:
            Complexity score (0-10+ range)
        """
        return self.last_complexity_score
