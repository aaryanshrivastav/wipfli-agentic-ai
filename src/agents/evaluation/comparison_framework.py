"""Agent Comparison Framework

Compares Rule-Based Agent vs Llama Agent side-by-side across scenarios.

This framework answers critical questions:
- How often do they agree?
- Where does the LLM add value?
- Which has better explanations?
- What are the latency/cost tradeoffs?

Usage:
    from evaluation.comparison_framework import compare_agents
    
    comparison = compare_agents(
        spark=spark,
        scenarios=[
            {"product_key": 101, "store_key": 5, "supplier_key": 42},
            {"product_key": 102, "store_key": 3, "supplier_key": 15}
        ]
    )
    
    print_comparison_summary(comparison)
"""

import time
from typing import Dict, Any, List
from datetime import datetime

from decision.base_agent import BaseSupplyChainAgent
from decision.rule_based_agent import RuleBasedAgent
from decision.llama_agent import LlamaSupplyChainAgent
from orchestrator.context_builder import build_agent_context
from orchestrator.tool_registry import TOOL_REGISTRY


class AgentComparison:
    """Container for agent comparison results."""
    
    def __init__(self):
        self.scenarios = []
        self.total_runs = 0
        self.agreement_count = 0
        self.rule_errors = 0
        self.llama_errors = 0
        self.start_time = None
        self.end_time = None
    
    def add_scenario_result(self, result: Dict[str, Any]):
        """Add a scenario comparison result."""
        self.scenarios.append(result)
        self.total_runs += 1
        
        if result["rule_decision"] and result["llama_decision"]:
            if result["rule_decision"]["action"] == result["llama_decision"]["action"]:
                self.agreement_count += 1
        
        if result["rule_error"]:
            self.rule_errors += 1
        if result["llama_error"]:
            self.llama_errors += 1
    
    def get_agreement_rate(self) -> float:
        """Calculate agreement rate between agents."""
        if self.total_runs == 0:
            return 0.0
        return self.agreement_count / self.total_runs
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comparison summary statistics."""
        return {
            "total_runs": self.total_runs,
            "agreement_count": self.agreement_count,
            "agreement_rate": self.get_agreement_rate(),
            "rule_errors": self.rule_errors,
            "llama_errors": self.llama_errors,
            "rule_success_rate": 1 - (self.rule_errors / self.total_runs) if self.total_runs > 0 else 0,
            "llama_success_rate": 1 - (self.llama_errors / self.total_runs) if self.total_runs > 0 else 0,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        }


def fetch_context_data(
    spark,
    product_key: int,
    store_key: int,
    supplier_key: int
) -> Dict[str, Any]:
    """Fetch context data for a scenario.
    
    Args:
        spark: SparkSession
        product_key: Product identifier
        store_key: Store identifier
        supplier_key: Supplier identifier
        
    Returns:
        Context dictionary
    """
    # Get inventory risk
    inventory_risk = TOOL_REGISTRY["get_inventory_risk"](
        spark, product_key, store_key
    )
    
    # Get supplier risk
    supplier_risk = TOOL_REGISTRY["get_supplier_risk"](
        spark, supplier_key
    )
    
    # Get forecast
    forecast = TOOL_REGISTRY["get_forecast"](
        spark, product_key, store_key
    )
    
    # Get previous recommendation
    recommendation = TOOL_REGISTRY["get_recommendation"](
        spark, product_key, store_key
    )
    
    # Get purchase orders
    purchase_orders = TOOL_REGISTRY["get_open_purchase_orders"](
        spark, product_key
    )
    
    # Build context
    context = build_agent_context(
        inventory_risk=inventory_risk,
        supplier_risk=supplier_risk,
        forecast=forecast,
        recommendation=recommendation,
        purchase_orders=purchase_orders
    )
    
    return context


def run_agent_with_timing(agent: BaseSupplyChainAgent, context: Dict[str, Any]) -> Dict[str, Any]:
    """Run agent and measure performance.
    
    Args:
        agent: Agent to run
        context: Context data
        
    Returns:
        Result dictionary with decision and metrics
    """
    start_time = time.time()
    error = None
    decision = None
    
    try:
        decision = agent.decide(context)
    except Exception as e:
        error = str(e)
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "decision": decision,
        "error": error,
        "latency_ms": latency_ms,
        "agent_name": agent.get_name()
    }


def compare_agents_on_scenario(
    spark,
    product_key: int,
    store_key: int,
    supplier_key: int,
    rule_agent: RuleBasedAgent = None,
    llama_agent: LlamaSupplyChainAgent = None
) -> Dict[str, Any]:
    """Compare both agents on a single scenario.
    
    Args:
        spark: SparkSession
        product_key: Product identifier
        store_key: Store identifier
        supplier_key: Supplier identifier
        rule_agent: Rule-based agent (creates new if None)
        llama_agent: Llama agent (creates new if None)
        
    Returns:
        Comparison result dictionary
    """
    # Create agents if not provided
    if rule_agent is None:
        rule_agent = RuleBasedAgent()
    if llama_agent is None:
        llama_agent = LlamaSupplyChainAgent()
    
    # Fetch context data
    context_start = time.time()
    context = fetch_context_data(spark, product_key, store_key, supplier_key)
    context_latency_ms = (time.time() - context_start) * 1000
    
    # Run rule agent
    rule_result = run_agent_with_timing(rule_agent, context)
    
    # Run Llama agent
    llama_result = run_agent_with_timing(llama_agent, context)
    
    # Compare decisions
    agreement = False
    if rule_result["decision"] and llama_result["decision"]:
        agreement = rule_result["decision"]["action"] == llama_result["decision"]["action"]
    
    return {
        "scenario": {
            "product_key": product_key,
            "store_key": store_key,
            "supplier_key": supplier_key
        },
        "context": context,
        "context_latency_ms": context_latency_ms,
        "rule_decision": rule_result["decision"],
        "rule_error": rule_result["error"],
        "rule_latency_ms": rule_result["latency_ms"],
        "llama_decision": llama_result["decision"],
        "llama_error": llama_result["error"],
        "llama_latency_ms": llama_result["latency_ms"],
        "agreement": agreement,
        "timestamp": datetime.now().isoformat()
    }


def compare_agents(
    spark,
    scenarios: List[Dict[str, int]]
) -> AgentComparison:
    """Compare agents across multiple scenarios.
    
    Args:
        spark: SparkSession
        scenarios: List of scenario dicts with product_key, store_key, supplier_key
        
    Returns:
        AgentComparison object with results
        
    Example:
        scenarios = [
            {"product_key": 101, "store_key": 5, "supplier_key": 42},
            {"product_key": 102, "store_key": 3, "supplier_key": 15}
        ]
        comparison = compare_agents(spark, scenarios)
    """
    comparison = AgentComparison()
    comparison.start_time = datetime.now()
    
    # Create agents once (reuse across scenarios)
    rule_agent = RuleBasedAgent()
    llama_agent = LlamaSupplyChainAgent()
    
    for scenario in scenarios:
        result = compare_agents_on_scenario(
            spark=spark,
            product_key=scenario["product_key"],
            store_key=scenario["store_key"],
            supplier_key=scenario["supplier_key"],
            rule_agent=rule_agent,
            llama_agent=llama_agent
        )
        comparison.add_scenario_result(result)
    
    comparison.end_time = datetime.now()
    
    return comparison


def print_comparison_summary(comparison: AgentComparison):
    """Print a formatted comparison summary.
    
    Args:
        comparison: AgentComparison object
    """
    summary = comparison.get_summary()
    
    print("="*70)
    print("AGENT COMPARISON SUMMARY")
    print("="*70)
    print(f"\nTotal Scenarios: {summary['total_runs']}")
    print(f"Agreement Rate: {summary['agreement_rate']:.1%}")
    print(f"Agreements: {summary['agreement_count']}/{summary['total_runs']}")
    print()
    print(f"Rule Agent Success Rate: {summary['rule_success_rate']:.1%}")
    print(f"Llama Agent Success Rate: {summary['llama_success_rate']:.1%}")
    print()
    print(f"Duration: {summary['duration_seconds']:.2f}s")
    print("="*70)
    
    # Print scenario details
    print("\nSCENARIO DETAILS:")
    print("="*70)
    
    for i, scenario in enumerate(comparison.scenarios, 1):
        print(f"\nScenario {i}:")
        print(f"  Product: {scenario['scenario']['product_key']}, "
              f"Store: {scenario['scenario']['store_key']}, "
              f"Supplier: {scenario['scenario']['supplier_key']}")
        
        # Rule agent
        if scenario['rule_decision']:
            print(f"  Rule Agent: {scenario['rule_decision']['action']} "
                  f"({scenario['rule_decision']['priority']}, "
                  f"conf={scenario['rule_decision']['confidence']:.2f}) "
                  f"[{scenario['rule_latency_ms']:.1f}ms]")
        else:
            print(f"  Rule Agent: ERROR - {scenario['rule_error']}")
        
        # Llama agent
        if scenario['llama_decision']:
            print(f"  Llama Agent: {scenario['llama_decision']['action']} "
                  f"({scenario['llama_decision']['priority']}, "
                  f"conf={scenario['llama_decision']['confidence']:.2f}) "
                  f"[{scenario['llama_latency_ms']:.1f}ms]")
        else:
            print(f"  Llama Agent: ERROR - {scenario['llama_error']}")
        
        # Agreement
        if scenario['agreement']:
            print("  ✓ AGREE")
        else:
            print("  ✗ DISAGREE")
    
    print("="*70)


def print_comparison_table(comparison: AgentComparison):
    """Print comparison results as a table.
    
    Args:
        comparison: AgentComparison object
    """
    print("\n" + "="*100)
    print(f"{'Scenario':<20} {'Rule Agent':<25} {'Llama Agent':<25} {'Agreement':<10}")
    print("="*100)
    
    for i, scenario in enumerate(comparison.scenarios, 1):
        scenario_desc = f"#{i} P{scenario['scenario']['product_key']}/S{scenario['scenario']['store_key']}"
        
        rule_action = scenario['rule_decision']['action'] if scenario['rule_decision'] else "ERROR"
        llama_action = scenario['llama_decision']['action'] if scenario['llama_decision'] else "ERROR"
        agreement = "✓" if scenario['agreement'] else "✗"
        
        print(f"{scenario_desc:<20} {rule_action:<25} {llama_action:<25} {agreement:<10}")
    
    print("="*100)
