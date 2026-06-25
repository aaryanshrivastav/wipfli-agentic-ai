"""Llama-Based Supply Chain Agent

LLM-powered decision engine using Databricks Foundation Models.

This agent uses Llama models to reason about supply chain decisions.
It receives structured context and produces structured JSON output.

Key Principles:
- NO direct data access (SQL, forecasting, risk computation)
- ONLY reasoning over pre-computed context
- Outputs ONLY structured JSON decisions
- Never hallucinates data or metrics
- Raises exceptions on failure (no fake fallback decisions)
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseSupplyChainAgent


class LlamaSupplyChainAgent(BaseSupplyChainAgent):
    """LLM-based supply chain decision agent using Databricks Foundation Models.
    
    Uses Llama models to make intelligent decisions based on structured context.
    The LLM's job is pure reasoning - all data retrieval and computation
    happens before this agent is invoked.
    
    V1.0 Behavior: If LLM fails, raises exception instead of returning fake decision.
    The hybrid agent catches this and properly falls back to rules.
    """
    
    def __init__(
        self,
        model_name: str = "databricks-meta-llama-3-3-70b-instruct",
        temperature: float = 0.1,
        max_tokens: int = 500
    ):
        """Initialize the Llama agent.
        
        Args:
            model_name: Databricks Foundation Model endpoint name
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.name = "llama_agent"
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for the LLM.
        
        Args:
            context: Structured context with all data
            
        Returns:
            Formatted prompt string
        """
        inventory = context.get("inventory_risk", {})
        supplier = context.get("supplier_risk", {})
        forecast = context.get("forecast", {})
        recommendation = context.get("recommendation", {})
        purchase_orders = context.get("purchase_orders", {})
        
        prompt = """You are a supply chain planner. Analyze the data below and make a decision.

INVENTORY RISK:
---------------
- Current Quantity: {inventory_qty}
- Risk Level: {inventory_risk_level}
- Days to Stockout: {days_to_stockout}
- 7-day Forecast Demand: {forecast_7d}
- 14-day Forecast Demand: {forecast_14d}
- 30-day Forecast Demand: {forecast_30d}

SUPPLIER RISK:
--------------
- Risk Level: {supplier_risk_level}
- On-Time Delivery Rate: {supplier_otd}%
- Quality Score: {supplier_quality}

PURCHASE ORDERS:
----------------
- Open PO Count: {open_po_count}

PREVIOUS RECOMMENDATION:
-----------------------
- Previous Action: {prev_action}
- Previous Reasoning: {prev_reasoning}

DECISION RULES:
---------------
Actions available:
- EXPEDITE_PO: Rush existing purchase orders (for imminent stockouts)
- REORDER: Place new order (for high inventory risk)
- SUPPLIER_ALERT: Flag supplier issues (for supplier risk)
- NO_ACTION: Continue monitoring (for healthy state)

Priority levels:
- CRITICAL: Immediate action required (stockout within 7 days)
- HIGH: Action needed soon (risk levels HIGH/CRITICAL)
- MEDIUM: Monitor closely
- LOW: Business as usual

Confidence scoring (0.0 to 1.0):
- 0.95-1.0: Very clear decision, strong supporting evidence
- 0.85-0.94: Clear decision, good supporting evidence
- 0.70-0.84: Reasonable decision, moderate supporting evidence
- 0.50-0.69: Uncertain decision, conflicting signals
- Below 0.50: Highly uncertain, recommend human review

Guidelines:
- Imminent stockout (< 7 days) = high confidence EXPEDITE_PO
- Risk levels CRITICAL/HIGH = high confidence action
- Conflicting signals (e.g., high inventory risk but supplier issues) = lower confidence
- Missing data = lower confidence

Return ONLY valid JSON in this exact format (no markdown, no explanation):

{{
  "action": "...",
  "priority": "...",
  "confidence": 0.0,
  "reasoning": "..."
}}""".format(
            inventory_qty=inventory.get("inventory_qty", "N/A"),
            inventory_risk_level=inventory.get("risk_level", "N/A"),
            days_to_stockout=inventory.get("projected_days_to_stockout", "N/A"),
            forecast_7d=forecast.get("forecast_7d", "N/A"),
            forecast_14d=forecast.get("forecast_14d", "N/A"),
            forecast_30d=forecast.get("forecast_30d", "N/A"),
            supplier_risk_level=supplier.get("risk_level", "N/A"),
            supplier_otd=supplier.get("on_time_delivery_rate", "N/A"),
            supplier_quality=supplier.get("quality_score", "N/A"),
            open_po_count=purchase_orders.get("open_po_count", 0),
            prev_action=recommendation.get("action", "None"),
            prev_reasoning=recommendation.get("reasoning", "No previous recommendation")
        )
        
        return prompt
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If no valid JSON found
        """
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Try to find JSON object in the text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        # Parse JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}\nResponse: {response_text}")
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a supply chain decision using Llama LLM.
        
        V1.0 Behavior: Raises exception on failure instead of returning fake decision.
        
        Args:
            context: Structured context with all data
            
        Returns:
            Decision dictionary with action, priority, confidence, reasoning
            
        Raises:
            Exception: If LLM call fails or returns invalid response
        """
        # Import Databricks SDK
        try:
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
        except ImportError:
            raise ImportError(
                "databricks-sdk not available. "
                "Install with: pip install databricks-sdk"
            )
        
        # Build prompt
        prompt = self._build_prompt(context)
        
        # Create WorkspaceClient (handles auth automatically in Databricks)
        w = WorkspaceClient()
        
        # V1.0: Let exceptions propagate to hybrid agent for proper fallback handling
        response = w.serving_endpoints.query(
            name=self.model_name,
            messages=[
                ChatMessage(
                    role=ChatMessageRole.SYSTEM,
                    content="You are a supply chain expert. Always respond with valid JSON only."
                ),
                ChatMessage(
                    role=ChatMessageRole.USER,
                    content=prompt
                )
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Extract response text
        response_text = response.choices[0].message.content
        
        # Parse JSON from response
        decision = self._extract_json_from_response(response_text)
        
        # Validate required fields
        required_fields = ["action", "priority", "confidence", "reasoning"]
        for field in required_fields:
            if field not in decision:
                raise ValueError(f"LLM response missing required field: {field}")
        
        # Ensure confidence is a float
        decision["confidence"] = float(decision["confidence"])
        
        return decision
    
    def get_name(self) -> str:
        """Return agent name."""
        return f"{self.name}_{self.model_name}"
