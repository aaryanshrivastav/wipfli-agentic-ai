"""Agent Context Builder

Builds rich context for agent decision-making.

Context includes:
- Current inventory risk state
- Supplier risk state
- Demand forecasts
- Open purchase orders
- Previous recommendation (if any)
- Recommendation history (last 3-5 actions)
- Previous outcome (accepted/rejected)

This rich context helps the agent:
- Avoid recommending the same action repeatedly
- Learn from past outcomes
- Understand temporal patterns
- Make more nuanced decisions
"""

from typing import Dict, Any


def build_agent_context(
    inventory_risk: Dict[str, Any],
    supplier_risk: Dict[str, Any],
    forecast: Dict[str, Any],
    recommendation: Dict[str, Any],
    purchase_orders: Dict[str, Any],
    recommendation_history: list = None,
    previous_outcome: str = None
) -> Dict[str, Any]:
    """Build structured context for agent decision-making.
    
    Args:
        inventory_risk: Current inventory risk data
        supplier_risk: Current supplier risk data
        forecast: Demand forecast data
        recommendation: Most recent recommendation (if any)
        purchase_orders: Open purchase order count
        recommendation_history: List of last 3-5 recommendations (optional)
        previous_outcome: Outcome of last recommendation (ACCEPTED/REJECTED/PENDING) (optional)
        
    Returns:
        Structured context dictionary
    """
    context = {
        "inventory_risk": inventory_risk or {},
        "supplier_risk": supplier_risk or {},
        "forecast": forecast or {},
        "recommendation": recommendation or {},
        "purchase_orders": purchase_orders or {},
        "recommendation_history": recommendation_history or [],
        "previous_outcome": previous_outcome
    }
    
    return context


def enrich_context_with_history(
    spark,
    context: Dict[str, Any],
    product_key: int,
    store_key: int,
    history_limit: int = 5
) -> Dict[str, Any]:
    """Enrich context with recommendation history.
    
    Args:
        spark: SparkSession
        context: Base context dictionary
        product_key: Product identifier
        store_key: Store identifier
        history_limit: Number of historical recommendations to include
        
    Returns:
        Enriched context with recommendation_history
    """
    # Query recommendation history
    history_query = f"""
    SELECT
        action_type,
        recommendation_reason,
        action_status,
        recommendation_timestamp
    FROM agentdb.silver.agent_action_log
    WHERE entity_type = 'inventory'
      AND entity_id = {product_key}
    ORDER BY recommendation_timestamp DESC
    LIMIT {history_limit}
    """
    
    history_rows = spark.sql(history_query).collect()
    
    recommendation_history = [
        {
            "action": row['action_type'],
            "reasoning": row['recommendation_reason'],
            "status": row['action_status'],
            "timestamp": str(row['recommendation_timestamp'])
        }
        for row in history_rows
    ]
    
    # Get previous outcome (most recent status)
    previous_outcome = None
    if recommendation_history:
        previous_outcome = recommendation_history[0]['status']
    
    context["recommendation_history"] = recommendation_history
    context["previous_outcome"] = previous_outcome
    
    return context
