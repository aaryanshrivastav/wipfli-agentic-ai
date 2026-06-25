"""Agent Performance Metrics Tracker

Computes and tracks performance metrics for agent evaluation.

Metrics tracked:
- Agent performance: latency, success rate, confidence, agreement
- Tool performance: latency, success rate, failure count
- Recommendation distribution: action types, priorities
- JSON validation rates

Usage:
    from evaluation.metrics_tracker import compute_agent_metrics
    
    metrics = compute_agent_metrics(spark, time_window="last_7_days")
    print_metrics_report(metrics)
"""

from typing import Dict, Any, List
from collections import Counter, defaultdict


def compute_agent_metrics_from_comparison(comparison) -> Dict[str, Any]:
    """Compute agent performance metrics from comparison results.
    
    Args:
        comparison: AgentComparison object
        
    Returns:
        Dictionary of agent metrics
    """
    if comparison.total_runs == 0:
        return {
            "total_runs": 0,
            "error": "No runs to analyze"
        }
    
    # Rule agent metrics
    rule_latencies = [s["rule_latency_ms"] for s in comparison.scenarios if s["rule_decision"]]
    rule_confidences = [s["rule_decision"]["confidence"] for s in comparison.scenarios if s["rule_decision"]]
    rule_actions = [s["rule_decision"]["action"] for s in comparison.scenarios if s["rule_decision"]]
    rule_priorities = [s["rule_decision"]["priority"] for s in comparison.scenarios if s["rule_decision"]]
    
    # Llama agent metrics
    llama_latencies = [s["llama_latency_ms"] for s in comparison.scenarios if s["llama_decision"]]
    llama_confidences = [s["llama_decision"]["confidence"] for s in comparison.scenarios if s["llama_decision"]]
    llama_actions = [s["llama_decision"]["action"] for s in comparison.scenarios if s["llama_decision"]]
    llama_priorities = [s["llama_decision"]["priority"] for s in comparison.scenarios if s["llama_decision"]]
    
    return {
        "total_runs": comparison.total_runs,
        "successful_runs": comparison.total_runs - comparison.rule_errors - comparison.llama_errors,
        "agreement_rate": comparison.get_agreement_rate(),
        "agreement_count": comparison.agreement_count,
        
        # Rule agent
        "rule_agent": {
            "success_rate": 1 - (comparison.rule_errors / comparison.total_runs),
            "avg_latency_ms": sum(rule_latencies) / len(rule_latencies) if rule_latencies else 0,
            "min_latency_ms": min(rule_latencies) if rule_latencies else 0,
            "max_latency_ms": max(rule_latencies) if rule_latencies else 0,
            "avg_confidence": sum(rule_confidences) / len(rule_confidences) if rule_confidences else 0,
            "action_distribution": dict(Counter(rule_actions)),
            "priority_distribution": dict(Counter(rule_priorities)),
            "error_count": comparison.rule_errors
        },
        
        # Llama agent
        "llama_agent": {
            "success_rate": 1 - (comparison.llama_errors / comparison.total_runs),
            "avg_latency_ms": sum(llama_latencies) / len(llama_latencies) if llama_latencies else 0,
            "min_latency_ms": min(llama_latencies) if llama_latencies else 0,
            "max_latency_ms": max(llama_latencies) if llama_latencies else 0,
            "avg_confidence": sum(llama_confidences) / len(llama_confidences) if llama_confidences else 0,
            "action_distribution": dict(Counter(llama_actions)),
            "priority_distribution": dict(Counter(llama_priorities)),
            "error_count": comparison.llama_errors
        }
    }


def compute_tool_metrics(spark, run_ids: List[str] = None) -> Dict[str, Any]:
    """Compute tool performance metrics from agent_tool_execution_log.
    
    Args:
        spark: SparkSession
        run_ids: Optional list of run IDs to filter on
        
    Returns:
        Dictionary of tool metrics
    """
    # Build query
    if run_ids and len(run_ids) > 0:
        run_id_filter = "WHERE run_id IN (" + ",".join([f"'{rid}'" for rid in run_ids]) + ")"
    else:
        run_id_filter = ""
    
    query = f"""
    SELECT
        tool_name,
        COUNT(*) as total_calls,
        SUM(CASE WHEN success_flag = true THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN success_flag = false THEN 1 ELSE 0 END) as failure_count,
        AVG(execution_duration_ms) as avg_latency_ms,
        MIN(execution_duration_ms) as min_latency_ms,
        MAX(execution_duration_ms) as max_latency_ms
    FROM agentdb.silver.agent_tool_execution_log
    {run_id_filter}
    GROUP BY tool_name
    ORDER BY tool_name
    """
    
    results = spark.sql(query).collect()
    
    tool_metrics = {}
    for row in results:
        tool_metrics[row['tool_name']] = {
            "total_calls": row['total_calls'],
            "success_count": row['success_count'],
            "failure_count": row['failure_count'],
            "success_rate": row['success_count'] / row['total_calls'] if row['total_calls'] > 0 else 0,
            "avg_latency_ms": float(row['avg_latency_ms']) if row['avg_latency_ms'] else 0,
            "min_latency_ms": float(row['min_latency_ms']) if row['min_latency_ms'] else 0,
            "max_latency_ms": float(row['max_latency_ms']) if row['max_latency_ms'] else 0
        }
    
    return tool_metrics


def compute_run_metrics(spark, time_window: str = None) -> Dict[str, Any]:
    """Compute run-level metrics from agent_run_log.
    
    Args:
        spark: SparkSession
        time_window: Optional time window filter (e.g., "last_7_days")
        
    Returns:
        Dictionary of run metrics
    """
    # Build time filter
    time_filter = ""
    if time_window == "last_7_days":
        time_filter = "WHERE run_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS"
    elif time_window == "last_24_hours":
        time_filter = "WHERE run_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY"
    
    query = f"""
    SELECT
        agent_name,
        COUNT(*) as total_runs,
        SUM(CASE WHEN run_status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
        SUM(CASE WHEN run_status = 'FAILED' THEN 1 ELSE 0 END) as failed_runs,
        AVG(execution_duration_ms) as avg_duration_ms,
        SUM(recommendations_generated) as total_recommendations,
        SUM(recommendations_accepted) as total_accepted,
        SUM(recommendations_rejected) as total_rejected
    FROM agentdb.silver.agent_run_log
    {time_filter}
    GROUP BY agent_name
    ORDER BY agent_name
    """
    
    results = spark.sql(query).collect()
    
    run_metrics = {}
    for row in results:
        run_metrics[row['agent_name']] = {
            "total_runs": row['total_runs'],
            "successful_runs": row['successful_runs'],
            "failed_runs": row['failed_runs'],
            "success_rate": row['successful_runs'] / row['total_runs'] if row['total_runs'] > 0 else 0,
            "avg_duration_ms": float(row['avg_duration_ms']) if row['avg_duration_ms'] else 0,
            "total_recommendations": row['total_recommendations'],
            "total_accepted": row['total_accepted'],
            "total_rejected": row['total_rejected'],
            "acceptance_rate": row['total_accepted'] / row['total_recommendations'] if row['total_recommendations'] > 0 else 0
        }
    
    return run_metrics


def print_metrics_report(metrics: Dict[str, Any]):
    """Print a formatted metrics report.
    
    Args:
        metrics: Metrics dictionary from compute_agent_metrics_from_comparison
    """
    print("="*80)
    print("AGENT PERFORMANCE METRICS")
    print("="*80)
    print()
    print(f"Total Runs: {metrics['total_runs']}")
    print(f"Successful Runs: {metrics['successful_runs']}")
    print(f"Agreement Rate: {metrics['agreement_rate']:.1%}")
    print()
    
    # Rule agent
    print("-"*80)
    print("RULE-BASED AGENT")
    print("-"*80)
    rule = metrics['rule_agent']
    print(f"Success Rate: {rule['success_rate']:.1%}")
    print(f"Avg Latency: {rule['avg_latency_ms']:.1f}ms")
    print(f"Latency Range: {rule['min_latency_ms']:.1f}ms - {rule['max_latency_ms']:.1f}ms")
    print(f"Avg Confidence: {rule['avg_confidence']:.2f}")
    print(f"Error Count: {rule['error_count']}")
    print()
    print("Action Distribution:")
    for action, count in rule['action_distribution'].items():
        print(f"  {action}: {count}")
    print()
    print("Priority Distribution:")
    for priority, count in rule['priority_distribution'].items():
        print(f"  {priority}: {count}")
    print()
    
    # Llama agent
    print("-"*80)
    print("LLAMA AGENT")
    print("-"*80)
    llama = metrics['llama_agent']
    print(f"Success Rate: {llama['success_rate']:.1%}")
    print(f"Avg Latency: {llama['avg_latency_ms']:.1f}ms")
    print(f"Latency Range: {llama['min_latency_ms']:.1f}ms - {llama['max_latency_ms']:.1f}ms")
    print(f"Avg Confidence: {llama['avg_confidence']:.2f}")
    print(f"Error Count: {llama['error_count']}")
    print()
    print("Action Distribution:")
    for action, count in llama['action_distribution'].items():
        print(f"  {action}: {count}")
    print()
    print("Priority Distribution:")
    for priority, count in llama['priority_distribution'].items():
        print(f"  {priority}: {count}")
    print("="*80)


def print_tool_metrics_report(tool_metrics: Dict[str, Any]):
    """Print a formatted tool metrics report.
    
    Args:
        tool_metrics: Tool metrics dictionary from compute_tool_metrics
    """
    print("\n" + "="*100)
    print("TOOL PERFORMANCE METRICS")
    print("="*100)
    print(f"{'Tool Name':<30} {'Avg Latency':<15} {'Success Rate':<15} {'Failure Count':<15}")
    print("-"*100)
    
    for tool_name, metrics in sorted(tool_metrics.items()):
        print(f"{tool_name:<30} "
              f"{metrics['avg_latency_ms']:>10.1f}ms    "
              f"{metrics['success_rate']:>10.1%}    "
              f"{metrics['failure_count']:>10}")
    
    print("="*100)


def compare_agent_differences(comparison) -> Dict[str, Any]:
    """Analyze where agents differ in their decisions.
    
    Args:
        comparison: AgentComparison object
        
    Returns:
        Dictionary of disagreement analysis
    """
    disagreements = [s for s in comparison.scenarios if not s['agreement']]
    
    if not disagreements:
        return {
            "total_disagreements": 0,
            "message": "All agents agree!"
        }
    
    # Analyze patterns in disagreements
    patterns = defaultdict(int)
    for d in disagreements:
        if d['rule_decision'] and d['llama_decision']:
            pattern = f"{d['rule_decision']['action']} → {d['llama_decision']['action']}"
            patterns[pattern] += 1
    
    # Find scenarios where Llama is more conservative
    llama_more_conservative = sum(1 for d in disagreements 
                                   if d['llama_decision'] and d['llama_decision']['action'] == 'NO_ACTION')
    
    # Find scenarios where Llama is more aggressive
    llama_more_aggressive = sum(1 for d in disagreements
                                 if d['rule_decision'] and d['rule_decision']['action'] == 'NO_ACTION')
    
    return {
        "total_disagreements": len(disagreements),
        "disagreement_rate": len(disagreements) / comparison.total_runs if comparison.total_runs > 0 else 0,
        "disagreement_patterns": dict(patterns),
        "llama_more_conservative": llama_more_conservative,
        "llama_more_aggressive": llama_more_aggressive,
        "examples": [
            {
                "scenario": d['scenario'],
                "rule_action": d['rule_decision']['action'] if d['rule_decision'] else None,
                "llama_action": d['llama_decision']['action'] if d['llama_decision'] else None,
                "rule_reasoning": d['rule_decision']['reasoning'] if d['rule_decision'] else None,
                "llama_reasoning": d['llama_decision']['reasoning'] if d['llama_decision'] else None
            }
            for d in disagreements[:3]  # Show first 3 examples
        ]
    }
