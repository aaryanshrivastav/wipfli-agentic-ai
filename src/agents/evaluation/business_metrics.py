"""Business Metrics for Supply Chain Agent

Tracks business-level impact metrics, not just technical metrics.

Operations managers care about:
- Stockouts prevented (revenue protection)
- Excess inventory avoided (cost reduction)
- Inventory carrying cost (financial impact - TRADEOFF)
- Service level (customer experience)
- Fill rate (supply chain KPI)

These metrics answer: "Did the agent improve the business?"

IMPORTANT: Carrying cost may INCREASE (not decrease) when avoiding stockouts.
This is a TRADEOFF: Revenue Protected vs Additional Carrying Cost.
We report NET VALUE, not "savings".

Usage:
    from evaluation.business_metrics import compute_business_impact
    
    impact = compute_business_impact(
        spark=spark,
        comparison=comparison,
        avg_product_value=50.0,
        carrying_cost_rate=0.25
    )
    
    print_business_impact_report(impact)
"""

from typing import Dict, Any, List


def estimate_stockouts_prevented(
    scenarios: List[Dict[str, Any]],
    avg_product_value: float = 50.0
) -> Dict[str, Any]:
    """Estimate stockouts prevented by agent recommendations.
    
    Args:
        scenarios: List of comparison scenarios
        avg_product_value: Average product value ($)
        
    Returns:
        Dictionary with stockout prevention metrics
    """
    stockouts_prevented = 0
    revenue_protected = 0.0
    
    for scenario in scenarios:
        context = scenario.get("context", {})
        inventory = context.get("inventory_risk", {})
        decision = scenario.get("rule_decision") or scenario.get("llama_decision")
        
        if not decision:
            continue
        
        # Count EXPEDITE_PO and REORDER actions when stockout risk is high
        days_to_stockout = inventory.get("projected_days_to_stockout")
        risk_level = inventory.get("risk_level")
        
        if decision["action"] in ["EXPEDITE_PO", "REORDER"]:
            if (days_to_stockout is not None and days_to_stockout < 14) or risk_level in ["HIGH", "CRITICAL"]:
                stockouts_prevented += 1
                # Estimate revenue protected
                forecast_7d = inventory.get("forecast_7d", 0)
                revenue_protected += forecast_7d * avg_product_value
    
    return {
        "stockouts_prevented": stockouts_prevented,
        "revenue_protected_usd": revenue_protected,
        "avg_revenue_per_prevented_stockout": revenue_protected / stockouts_prevented if stockouts_prevented > 0 else 0
    }


def estimate_excess_inventory_avoided(
    scenarios: List[Dict[str, Any]],
    avg_product_value: float = 50.0
) -> Dict[str, Any]:
    """Estimate excess inventory avoided by NOT over-ordering.
    
    Args:
        scenarios: List of comparison scenarios
        avg_product_value: Average product value ($)
        
    Returns:
        Dictionary with excess inventory metrics
    """
    excess_avoided_units = 0
    cost_avoided = 0.0
    
    for scenario in scenarios:
        context = scenario.get("context", {})
        inventory = context.get("inventory_risk", {})
        decision = scenario.get("rule_decision") or scenario.get("llama_decision")
        
        if not decision:
            continue
        
        # Count NO_ACTION when inventory is healthy (avoided unnecessary orders)
        risk_level = inventory.get("risk_level")
        inventory_qty = inventory.get("inventory_qty", 0)
        forecast_7d = inventory.get("forecast_7d", 0)
        
        if decision["action"] == "NO_ACTION" and risk_level == "LOW":
            # Estimate units that would have been ordered unnecessarily
            # Assume standard reorder would be 2 weeks of demand
            unnecessary_units = forecast_7d * 2 - inventory_qty
            if unnecessary_units > 0:
                excess_avoided_units += unnecessary_units
                cost_avoided += unnecessary_units * avg_product_value
    
    return {
        "excess_inventory_avoided_units": excess_avoided_units,
        "cost_avoided_usd": cost_avoided
    }


def estimate_carrying_cost_impact(
    scenarios: List[Dict[str, Any]],
    avg_product_value: float = 50.0,
    carrying_cost_rate: float = 0.25
) -> Dict[str, Any]:
    """Estimate inventory carrying cost impact (TRADEOFF ANALYSIS).
    
    IMPORTANT: Carrying cost may INCREASE when avoiding stockouts.
    This is intentional - we hold more inventory to protect revenue.
    
    Returns both baseline and optimized carrying costs, plus the NET VALUE
    (revenue protected - additional carrying cost).
    
    Args:
        scenarios: List of comparison scenarios
        avg_product_value: Average product value ($)
        carrying_cost_rate: Annual carrying cost rate (e.g., 0.25 = 25%)
        
    Returns:
        Dictionary with carrying cost metrics including tradeoff analysis
    """
    # Carrying cost = inventory_value * carrying_cost_rate * time_period
    # For weekly decisions, time_period = 1/52
    
    total_inventory_value = 0.0
    optimized_inventory_value = 0.0
    
    for scenario in scenarios:
        context = scenario.get("context", {})
        inventory = context.get("inventory_risk", {})
        decision = scenario.get("rule_decision") or scenario.get("llama_decision")
        
        if not decision:
            continue
        
        inventory_qty = inventory.get("inventory_qty", 0)
        forecast_7d = inventory.get("forecast_7d", 0)
        
        # Current inventory value
        current_value = inventory_qty * avg_product_value
        total_inventory_value += current_value
        
        # Optimized inventory (after agent decision)
        if decision["action"] == "REORDER":
            # Reorder adds 2 weeks of demand
            optimized_value = (inventory_qty + forecast_7d * 2) * avg_product_value
        elif decision["action"] == "EXPEDITE_PO":
            # Expedite adds 1 week of demand faster
            optimized_value = (inventory_qty + forecast_7d) * avg_product_value
        else:
            # NO_ACTION or SUPPLIER_ALERT maintains current inventory
            optimized_value = current_value
        
        optimized_inventory_value += optimized_value
    
    # Calculate weekly carrying cost
    weekly_carrying_rate = carrying_cost_rate / 52
    
    baseline_carrying_cost = total_inventory_value * weekly_carrying_rate
    optimized_carrying_cost = optimized_inventory_value * weekly_carrying_rate
    carrying_cost_delta = optimized_carrying_cost - baseline_carrying_cost
    
    return {
        "baseline_carrying_cost_usd_weekly": baseline_carrying_cost,
        "optimized_carrying_cost_usd_weekly": optimized_carrying_cost,
        "carrying_cost_delta_usd_weekly": carrying_cost_delta,
        "carrying_cost_delta_usd_annual": carrying_cost_delta * 52,
        "is_tradeoff": carrying_cost_delta > 0  # True if we're paying more to hold inventory
    }


def estimate_service_level(
    scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Estimate service level (% of demand met without stockout).
    
    Args:
        scenarios: List of comparison scenarios
        
    Returns:
        Dictionary with service level metrics
    """
    scenarios_at_risk = 0
    scenarios_addressed = 0
    
    for scenario in scenarios:
        context = scenario.get("context", {})
        inventory = context.get("inventory_risk", {})
        decision = scenario.get("rule_decision") or scenario.get("llama_decision")
        
        if not decision:
            continue
        
        # Count scenarios at risk of stockout
        days_to_stockout = inventory.get("projected_days_to_stockout")
        if days_to_stockout is not None and days_to_stockout < 14:
            scenarios_at_risk += 1
            
            # Did agent take action?
            if decision["action"] in ["EXPEDITE_PO", "REORDER"]:
                scenarios_addressed += 1
    
    service_level = scenarios_addressed / scenarios_at_risk if scenarios_at_risk > 0 else 1.0
    
    return {
        "scenarios_at_risk": scenarios_at_risk,
        "scenarios_addressed": scenarios_addressed,
        "estimated_service_level": service_level,
        "estimated_service_level_pct": service_level * 100
    }


def estimate_fill_rate(
    scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Estimate fill rate (% of demand fulfilled from stock).
    
    Args:
        scenarios: List of comparison scenarios
        
    Returns:
        Dictionary with fill rate metrics
    """
    total_demand = 0
    demand_fulfilled = 0
    
    for scenario in scenarios:
        context = scenario.get("context", {})
        inventory = context.get("inventory_risk", {})
        decision = scenario.get("rule_decision") or scenario.get("llama_decision")
        
        if not decision:
            continue
        
        inventory_qty = inventory.get("inventory_qty", 0)
        forecast_7d = inventory.get("forecast_7d", 0)
        
        if forecast_7d > 0:
            total_demand += forecast_7d
            
            # Can we fulfill demand from current + reordered inventory?
            if decision["action"] == "REORDER":
                available = inventory_qty + forecast_7d * 2  # Reorder adds 2 weeks
            elif decision["action"] == "EXPEDITE_PO":
                available = inventory_qty + forecast_7d  # Expedite adds 1 week
            else:
                available = inventory_qty
            
            # Fulfill as much demand as possible
            fulfilled = min(available, forecast_7d)
            demand_fulfilled += fulfilled
    
    fill_rate = demand_fulfilled / total_demand if total_demand > 0 else 1.0
    
    return {
        "total_demand_units": total_demand,
        "demand_fulfilled_units": demand_fulfilled,
        "estimated_fill_rate": fill_rate,
        "estimated_fill_rate_pct": fill_rate * 100
    }


def compute_business_impact(
    comparison,
    avg_product_value: float = 50.0,
    carrying_cost_rate: float = 0.25
) -> Dict[str, Any]:
    """Compute comprehensive business impact metrics.
    
    Args:
        comparison: AgentComparison object
        avg_product_value: Average product value ($)
        carrying_cost_rate: Annual inventory carrying cost rate
        
    Returns:
        Dictionary with all business impact metrics including NET VALUE
    """
    scenarios = comparison.scenarios
    
    stockouts = estimate_stockouts_prevented(scenarios, avg_product_value)
    excess = estimate_excess_inventory_avoided(scenarios, avg_product_value)
    carrying = estimate_carrying_cost_impact(scenarios, avg_product_value, carrying_cost_rate)
    service = estimate_service_level(scenarios)
    fill = estimate_fill_rate(scenarios)
    
    # Compute NET VALUE (revenue protected - additional carrying cost)
    revenue_protected = stockouts['revenue_protected_usd']
    carrying_cost_delta_annual = carrying['carrying_cost_delta_usd_annual']
    
    net_value_annual = revenue_protected - carrying_cost_delta_annual
    
    return {
        "stockouts": stockouts,
        "excess_inventory": excess,
        "carrying_cost": carrying,
        "service_level": service,
        "fill_rate": fill,
        "net_value_annual": net_value_annual
    }


def print_business_impact_report(impact: Dict[str, Any]):
    """Print formatted business impact report.
    
    Args:
        impact: Business impact dictionary from compute_business_impact
    """
    print("\n" + "="*80)
    print("BUSINESS IMPACT METRICS")
    print("="*80)
    
    # Stockouts prevented
    stockouts = impact["stockouts"]
    print("\n1. STOCKOUTS PREVENTED")
    print(f"   Count: {stockouts['stockouts_prevented']}")
    print(f"   Revenue Protected: ${stockouts['revenue_protected_usd']:,.2f}")
    print(f"   Avg per Prevented Stockout: ${stockouts['avg_revenue_per_prevented_stockout']:,.2f}")
    
    # Excess inventory avoided
    excess = impact["excess_inventory"]
    print("\n2. EXCESS INVENTORY AVOIDED")
    print(f"   Units: {excess['excess_inventory_avoided_units']:,.0f}")
    print(f"   Cost Avoided: ${excess['cost_avoided_usd']:,.2f}")
    
    # Carrying cost (TRADEOFF ANALYSIS)
    carrying = impact["carrying_cost"]
    print("\n3. INVENTORY CARRYING COST (TRADEOFF ANALYSIS)")
    print(f"   Baseline (Weekly): ${carrying['baseline_carrying_cost_usd_weekly']:,.2f}")
    print(f"   Optimized (Weekly): ${carrying['optimized_carrying_cost_usd_weekly']:,.2f}")
    
    if carrying['is_tradeoff']:
        # Carrying cost INCREASED (we're holding more inventory)
        print(f"   Additional Carrying Cost (Annual): ${carrying['carrying_cost_delta_usd_annual']:,.2f}")
        print(f"   → Agent increased inventory to avoid stockouts (intentional tradeoff)")
    else:
        # Carrying cost DECREASED (we're holding less inventory)
        print(f"   Carrying Cost Savings (Annual): ${-carrying['carrying_cost_delta_usd_annual']:,.2f}")
        print(f"   → Agent reduced excess inventory")
    
    # Service level
    service = impact["service_level"]
    print("\n4. SERVICE LEVEL")
    print(f"   Scenarios at Risk: {service['scenarios_at_risk']}")
    print(f"   Scenarios Addressed: {service['scenarios_addressed']}")
    print(f"   Estimated Service Level: {service['estimated_service_level_pct']:.1f}%")
    
    # Fill rate
    fill = impact["fill_rate"]
    print("\n5. FILL RATE")
    print(f"   Total Demand: {fill['total_demand_units']:,.0f} units")
    print(f"   Demand Fulfilled: {fill['demand_fulfilled_units']:,.0f} units")
    print(f"   Estimated Fill Rate: {fill['estimated_fill_rate_pct']:.1f}%")
    
    # NET VALUE CALCULATION
    print("\n" + "="*80)
    print("NET VALUE CALCULATION")
    print("="*80)
    print(f"Revenue Protected:              ${stockouts['revenue_protected_usd']:,.2f}")
    
    if carrying['is_tradeoff']:
        print(f"Additional Carrying Cost:      -${carrying['carrying_cost_delta_usd_annual']:,.2f}")
    else:
        print(f"Carrying Cost Savings:         +${-carrying['carrying_cost_delta_usd_annual']:,.2f}")
    
    print("-" * 80)
    net_value = impact['net_value_annual']
    print(f"NET VALUE (Annual):             ${net_value:,.2f}")
    print("="*80)
    
    if carrying['is_tradeoff']:
        print("\n⚠ TRADEOFF ANALYSIS:")
        print("  The agent increased inventory carrying costs to prevent stockouts.")
        print("  This is EXPECTED behavior when protecting revenue.")
        print(f"  Net benefit: ${net_value:,.2f} (revenue protected minus additional cost)")
