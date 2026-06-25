"""Decision Explanation Layer

Rich provenance tracking for supply chain agent decisions.

For every recommendation, captures:
- Decision source (which agent made it)
- Decision version (reproducibility)
- Tools used (which data sources contributed)
- Facts extracted (which values drove the decision)
- Reasoning (why this action was chosen)
- Confidence (how certain the agent is)

This enables:
- Audit trail for compliance
- Debugging incorrect decisions
- Reproducibility of recommendations
- Root cause analysis
- Trust and transparency

Usage:
    from evaluation.decision_explanation import create_decision_explanation
    
    explanation = create_decision_explanation(
        decision=decision,
        context=context,
        tools_used=["get_inventory_risk", "get_supplier_risk"],
        agent_version="1.0.0"
    )
    
    save_decision_explanation(spark, explanation, product_key, store_key)
"""

from typing import Dict, Any, List
from datetime import datetime


def create_decision_explanation(
    decision: Dict[str, Any],
    context: Dict[str, Any],
    tools_used: List[str],
    agent_version: str = "1.0.0"
) -> Dict[str, Any]:
    """Create rich decision explanation with full provenance.
    
    Args:
        decision: Agent decision dictionary
        context: Decision context (all data provided to agent)
        tools_used: List of tool names that contributed data
        agent_version: Version of the decision logic
        
    Returns:
        Explanation dictionary with full provenance
    """
    # Extract decision metadata
    decision_source = decision.get("decision_engine", "unknown")
    engine_status = decision.get("engine_status", "unknown")
    complexity_score = decision.get("complexity_score", None)
    
    # Extract key facts that drove the decision
    facts = extract_decision_facts(context)
    
    # Build explanation
    explanation = {
        "decision_source": decision_source,
        "engine_status": engine_status,
        "decision_version": agent_version,
        "complexity_score": complexity_score,
        "tools_used": tools_used,
        "facts": facts,
        "decision": {
            "action": decision.get("action"),
            "priority": decision.get("priority"),
            "confidence": decision.get("confidence"),
            "reasoning": decision.get("reasoning")
        },
        "fallback_info": {
            "fallback_occurred": decision.get("decision_engine") == "rule_fallback",
            "fallback_reason": decision.get("fallback_reason"),
            "attempted_engine": decision.get("attempted_engine")
        } if decision.get("decision_engine") == "rule_fallback" else None,
        "timestamp": datetime.now().isoformat(),
        "reproducible": True  # Can this decision be reproduced with the same inputs?
    }
    
    return explanation


def extract_decision_facts(context: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key facts from context that drove the decision.
    
    Args:
        context: Decision context
        
    Returns:
        Dictionary of key facts
    """
    inventory = context.get("inventory_risk", {})
    supplier = context.get("supplier_risk", {})
    forecast = context.get("forecast", {})
    purchase_orders = context.get("purchase_orders", {})
    recommendation_history = context.get("recommendation_history", [])
    
    facts = {
        "inventory": {
            "risk_level": inventory.get("risk_level"),
            "projected_days_to_stockout": inventory.get("projected_days_to_stockout"),
            "inventory_qty": inventory.get("inventory_qty"),
            "reorder_point": inventory.get("reorder_point"),
            "reorder_qty": inventory.get("reorder_qty")
        },
        "supplier": {
            "risk_level": supplier.get("risk_level"),
            "on_time_delivery_rate": supplier.get("on_time_delivery_rate"),
            "quality_score": supplier.get("quality_score"),
            "lead_time_days": supplier.get("lead_time_days")
        },
        "forecast": {
            "forecast_7d": forecast.get("forecast_7d"),
            "forecast_14d": forecast.get("forecast_14d"),
            "forecast_30d": forecast.get("forecast_30d"),
            "uncertainty": forecast.get("uncertainty")
        },
        "purchase_orders": {
            "open_po_count": purchase_orders.get("open_po_count")
        },
        "history": {
            "previous_recommendation_count": len(recommendation_history),
            "previous_actions": [h.get("action") for h in recommendation_history[:3]],
            "previous_outcome": context.get("previous_outcome")
        }
    }
    
    return facts


def save_decision_explanation(
    spark,
    explanation: Dict[str, Any],
    product_key: int,
    store_key: int,
    run_id: str = None
):
    """Save decision explanation to database for audit trail.
    
    Args:
        spark: SparkSession
        explanation: Decision explanation dictionary
        product_key: Product identifier
        store_key: Store identifier
        run_id: Optional run identifier for batch tracking
    """
    # Convert to JSON string for storage
    import json
    explanation_json = json.dumps(explanation)
    
    # Insert into decision_explanation table
    insert_query = f"""
    INSERT INTO agentdb.silver.decision_explanation
    (
        product_key,
        store_key,
        run_id,
        decision_source,
        engine_status,
        decision_version,
        complexity_score,
        action,
        priority,
        confidence,
        reasoning,
        tools_used,
        facts_json,
        explanation_json,
        fallback_occurred,
        fallback_reason,
        timestamp
    )
    VALUES (
        {product_key},
        {store_key},
        {f"'{run_id}'" if run_id else "NULL"},
        '{explanation['decision_source']}',
        '{explanation['engine_status']}',
        '{explanation['decision_version']}',
        {explanation['complexity_score'] if explanation['complexity_score'] is not None else "NULL"},
        '{explanation['decision']['action']}',
        '{explanation['decision']['priority']}',
        {explanation['decision']['confidence']},
        '{explanation['decision']['reasoning'].replace("'", "''")}',
        '{json.dumps(explanation['tools_used'])}',
        '{json.dumps(explanation['facts']).replace("'", "''")}',
        '{explanation_json.replace("'", "''")}',
        {explanation['fallback_info'] is not None if explanation['fallback_info'] else False},
        {f"'{explanation['fallback_info']['fallback_reason']}'" if explanation.get('fallback_info') and explanation['fallback_info'].get('fallback_reason') else "NULL"},
        CURRENT_TIMESTAMP
    )
    """
    
    spark.sql(insert_query)


def query_decision_explanations(
    spark,
    product_key: int = None,
    store_key: int = None,
    decision_source: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Query decision explanations from database.
    
    Args:
        spark: SparkSession
        product_key: Filter by product (optional)
        store_key: Filter by store (optional)
        decision_source: Filter by decision source (rule, llama, rule_fallback) (optional)
        start_date: Start date filter (YYYY-MM-DD) (optional)
        end_date: End date filter (YYYY-MM-DD) (optional)
        limit: Max rows to return
        
    Returns:
        List of decision explanation dictionaries
    """
    where_clauses = []
    
    if product_key:
        where_clauses.append(f"product_key = {product_key}")
    if store_key:
        where_clauses.append(f"store_key = {store_key}")
    if decision_source:
        where_clauses.append(f"decision_source = '{decision_source}'")
    if start_date:
        where_clauses.append(f"DATE(timestamp) >= '{start_date}'")
    if end_date:
        where_clauses.append(f"DATE(timestamp) <= '{end_date}'")
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f"""
    SELECT *
    FROM agentdb.silver.decision_explanation
    WHERE {where_sql}
    ORDER BY timestamp DESC
    LIMIT {limit}
    """
    
    rows = spark.sql(query).collect()
    
    # Convert to list of dictionaries
    import json
    explanations = []
    for row in rows:
        exp = {
            "product_key": row['product_key'],
            "store_key": row['store_key'],
            "decision_source": row['decision_source'],
            "engine_status": row['engine_status'],
            "decision_version": row['decision_version'],
            "complexity_score": row['complexity_score'],
            "action": row['action'],
            "priority": row['priority'],
            "confidence": row['confidence'],
            "reasoning": row['reasoning'],
            "tools_used": json.loads(row['tools_used']),
            "facts": json.loads(row['facts_json']),
            "fallback_occurred": row['fallback_occurred'],
            "fallback_reason": row['fallback_reason'],
            "timestamp": str(row['timestamp'])
        }
        explanations.append(exp)
    
    return explanations


def print_decision_explanation(explanation: Dict[str, Any]):
    """Print formatted decision explanation.
    
    Args:
        explanation: Decision explanation dictionary
    """
    print("\n" + "="*80)
    print("DECISION EXPLANATION")
    print("="*80)
    
    print("\nDECISION METADATA:")
    print(f"  Source:           {explanation['decision_source'].upper()}")
    print(f"  Status:           {explanation['engine_status']}")
    print(f"  Version:          {explanation['decision_version']}")
    print(f"  Complexity Score: {explanation['complexity_score']:.2f}" if explanation['complexity_score'] is not None else "  Complexity Score: N/A")
    print(f"  Timestamp:        {explanation['timestamp']}")
    
    # Fallback info
    if explanation.get('fallback_info'):
        print("\nFALLBACK DETAILS:")
        print(f"  Fallback Occurred: {explanation['fallback_info']['fallback_occurred']}")
        print(f"  Attempted Engine:  {explanation['fallback_info']['attempted_engine']}")
        print(f"  Fallback Reason:   {explanation['fallback_info']['fallback_reason']}")
    
    print("\nTOOLS USED:")
    for tool in explanation['tools_used']:
        print(f"  - {tool}")
    
    print("\nKEY FACTS:")
    facts = explanation['facts']
    
    print("  Inventory:")
    for key, value in facts['inventory'].items():
        print(f"    {key}: {value}")
    
    print("  Supplier:")
    for key, value in facts['supplier'].items():
        print(f"    {key}: {value}")
    
    print("  Forecast:")
    for key, value in facts['forecast'].items():
        print(f"    {key}: {value}")
    
    print("  Purchase Orders:")
    for key, value in facts['purchase_orders'].items():
        print(f"    {key}: {value}")
    
    print("  History:")
    for key, value in facts['history'].items():
        print(f"    {key}: {value}")
    
    print("\nDECISION:")
    decision = explanation['decision']
    print(f"  Action:     {decision['action']}")
    print(f"  Priority:   {decision['priority']}")
    print(f"  Confidence: {decision['confidence']:.2f}")
    print(f"  Reasoning:  {decision['reasoning']}")
    
    print("\nREPRODUCIBILITY:")
    print(f"  Can be reproduced: {explanation['reproducible']}")
    print(f"  → Run with decision version {explanation['decision_version']}")
    print(f"  → Use tools: {', '.join(explanation['tools_used'])}")
    print(f"  → With the same facts above")
    
    print("="*80)


def analyze_decision_patterns(
    spark,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Analyze decision patterns from explanation history.
    
    Args:
        spark: SparkSession
        start_date: Start date filter (YYYY-MM-DD) (optional)
        end_date: End date filter (YYYY-MM-DD) (optional)
        
    Returns:
        Dictionary with pattern analysis
    """
    where_clauses = ["1=1"]
    if start_date:
        where_clauses.append(f"DATE(timestamp) >= '{start_date}'")
    if end_date:
        where_clauses.append(f"DATE(timestamp) <= '{end_date}'")
    where_sql = " AND ".join(where_clauses)
    
    # Engine usage
    engine_usage = spark.sql(f"""
    SELECT
        decision_source,
        engine_status,
        COUNT(*) as count
    FROM agentdb.silver.decision_explanation
    WHERE {where_sql}
    GROUP BY decision_source, engine_status
    ORDER BY count DESC
    """).collect()
    
    # Average complexity by action
    complexity_by_action = spark.sql(f"""
    SELECT
        action,
        AVG(complexity_score) as avg_complexity,
        AVG(confidence) as avg_confidence,
        COUNT(*) as count
    FROM agentdb.silver.decision_explanation
    WHERE {where_sql} AND complexity_score IS NOT NULL
    GROUP BY action
    ORDER BY avg_complexity DESC
    """).collect()
    
    # Fallback rate
    fallback_stats = spark.sql(f"""
    SELECT
        COUNT(*) as total_decisions,
        SUM(CASE WHEN fallback_occurred THEN 1 ELSE 0 END) as fallback_count,
        SUM(CASE WHEN fallback_occurred THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as fallback_rate_pct
    FROM agentdb.silver.decision_explanation
    WHERE {where_sql}
    """).collect()[0]
    
    return {
        "engine_usage": [
            {"source": row['decision_source'], "status": row['engine_status'], "count": row['count']}
            for row in engine_usage
        ],
        "complexity_by_action": [
            {
                "action": row['action'],
                "avg_complexity": row['avg_complexity'],
                "avg_confidence": row['avg_confidence'],
                "count": row['count']
            }
            for row in complexity_by_action
        ],
        "fallback_stats": {
            "total_decisions": fallback_stats['total_decisions'],
            "fallback_count": fallback_stats['fallback_count'],
            "fallback_rate_pct": fallback_stats['fallback_rate_pct']
        }
    }


def print_decision_patterns(patterns: Dict[str, Any]):
    """Print formatted decision pattern analysis.
    
    Args:
        patterns: Pattern analysis from analyze_decision_patterns
    """
    print("\n" + "="*80)
    print("DECISION PATTERN ANALYSIS")
    print("="*80)
    
    print("\n1. ENGINE USAGE:")
    for entry in patterns['engine_usage']:
        print(f"   {entry['source'].upper()} ({entry['status']}): {entry['count']}")
    
    print("\n2. COMPLEXITY BY ACTION:")
    for entry in patterns['complexity_by_action']:
        print(f"   {entry['action']}:")
        print(f"     Avg Complexity: {entry['avg_complexity']:.2f}")
        print(f"     Avg Confidence: {entry['avg_confidence']:.2f}")
        print(f"     Count: {entry['count']}")
    
    print("\n3. FALLBACK STATISTICS:")
    stats = patterns['fallback_stats']
    print(f"   Total Decisions: {stats['total_decisions']}")
    print(f"   Fallback Count: {stats['fallback_count']}")
    print(f"   Fallback Rate: {stats['fallback_rate_pct']:.2f}%")
    
    if stats['fallback_rate_pct'] > 10:
        print("\n   ⚠ WARNING: Fallback rate is high (>10%)")
        print("   → LLM may be failing validation frequently")
        print("   → Review LLM prompt and validation logic")
    
    print("="*80)
