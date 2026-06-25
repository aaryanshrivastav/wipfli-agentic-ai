# Agent Evaluation & Comparison Framework

## Overview

The evaluation framework compares **Rule-Based Agent** vs **Llama Agent** side-by-side to answer critical questions:

- ✅ **How often do they agree?** (Agreement rate)
- ✅ **Where does the LLM add value?** (Disagreement analysis)
- ✅ **Which has better explanations?** (Reasoning quality)
- ✅ **What are the latency/cost tradeoffs?** (Performance metrics)

## Architecture

```
evaluation/
├── comparison_framework.py    # Side-by-side agent comparison
├── metrics_tracker.py         # Performance metrics computation
└── README.md                   # This file

tests/
└── test_agent_comparison.py   # Comprehensive comparison test
```

---

## Quick Start

### Run Comparison

```python
from evaluation.comparison_framework import compare_agents

# Define scenarios
scenarios = [
    {"product_key": 101, "store_key": 5, "supplier_key": 42},
    {"product_key": 102, "store_key": 3, "supplier_key": 15},
    {"product_key": 103, "store_key": 7, "supplier_key": 42}
]

# Run comparison
comparison = compare_agents(spark, scenarios)

# Print results
from evaluation.comparison_framework import print_comparison_summary, print_comparison_table
print_comparison_summary(comparison)
print_comparison_table(comparison)
```

### Compute Metrics

```python
from evaluation.metrics_tracker import (
    compute_agent_metrics_from_comparison,
    print_metrics_report
)

# Compute metrics from comparison
metrics = compute_agent_metrics_from_comparison(comparison)
print_metrics_report(metrics)
```

### Analyze Disagreements

```python
from evaluation.metrics_tracker import compare_agent_differences

# Analyze where agents differ
disagreements = compare_agent_differences(comparison)

print(f"Total disagreements: {disagreements['total_disagreements']}")
print(f"Disagreement patterns: {disagreements['disagreement_patterns']}")
```

---

## Metrics Tracked

### 1. Agent Performance Metrics

| Metric | Description |
|--------|-------------|
| `total_runs` | Number of agent executions |
| `successful_runs` | Completed without errors |
| `average_latency_ms` | End-to-end runtime per decision |
| `confidence_avg` | Average confidence score (0-1) |
| `agreement_rate` | % of cases where Rule and Llama agree |
| `valid_json_rate` | % of Llama responses that passed schema validation |
| `recommendation_distribution` | Distribution of actions (REORDER, EXPEDITE_PO, etc.) |

**Example Output:**

```
AGENT PERFORMANCE METRICS
========================================
Total Runs: 50
Successful Runs: 48
Agreement Rate: 82.0%

RULE-BASED AGENT
----------------------------------------
Success Rate: 100.0%
Avg Latency: 12.3ms
Avg Confidence: 0.92
Action Distribution:
  REORDER: 15
  EXPEDITE_PO: 8
  SUPPLIER_ALERT: 5
  NO_ACTION: 22

LLAMA AGENT
----------------------------------------
Success Rate: 96.0%
Avg Latency: 847.2ms
Avg Confidence: 0.78
Action Distribution:
  REORDER: 12
  EXPEDITE_PO: 10
  SUPPLIER_ALERT: 6
  NO_ACTION: 20
```

---

### 2. Tool Performance Metrics

| Metric | Description |
|--------|-------------|
| `avg_latency` | Average tool execution time |
| `success_rate` | % of successful tool calls |
| `failure_count` | Number of failed tool calls |

**Example Output:**

```
TOOL PERFORMANCE METRICS
================================================================================
Tool Name                      Avg Latency     Success Rate    Failure Count
--------------------------------------------------------------------------------
get_inventory_risk                  145.2ms          100.0%                0
get_supplier_risk                    98.3ms          100.0%                0
get_forecast                        132.7ms          100.0%                0
get_recommendation                  187.4ms           98.0%                1
get_open_purchase_orders             76.1ms          100.0%                0
================================================================================
```

---

### 3. Comparison Table

Visual side-by-side comparison of agent decisions:

```
Scenario             Rule Agent                Llama Agent               Agreement
====================================================================================================
#1 P101/S5          EXPEDITE_PO               EXPEDITE_PO               ✓
#2 P102/S3          REORDER                   REORDER                   ✓
#3 P103/S7          NO_ACTION                 SUPPLIER_ALERT            ✗
#4 P104/S2          SUPPLIER_ALERT            EXPEDITE_PO + ALERT       ✗
#5 P105/S9          NO_ACTION                 NO_ACTION                 ✓
====================================================================================================
```

---

## Disagreement Analysis

When agents disagree, the framework analyzes:

### Patterns

```
Disagreement Patterns:
  NO_ACTION → SUPPLIER_ALERT: 5 cases
  REORDER → EXPEDITE_PO: 3 cases
  SUPPLIER_ALERT → EXPEDITE_PO + ALERT: 2 cases
```

### Conservatism

```
Llama More Conservative: 3 cases
Llama More Aggressive: 7 cases
```

### Examples

```
Example 1:
  Scenario: Product 103, Store 7
  Rule Agent: NO_ACTION
    Reasoning: Inventory levels healthy.
  Llama Agent: SUPPLIER_ALERT
    Reasoning: Supplier on-time delivery dropped to 85% - proactive monitoring recommended.
```

**Key Insight:** Llama may catch nuanced patterns that rules miss.

---

## Use Cases

### 1. Baseline Establishment

Run rule agent on historical data to establish baseline performance:

```python
# Run rule agent only
from decision.rule_based_agent import RuleBasedAgent
agent = RuleBasedAgent()

for scenario in historical_scenarios:
    result = agent.decide(scenario['context'])
    # Log to database for analysis
```

**Goal:** Understand current decision patterns before introducing LLM.

---

### 2. A/B Testing Preparation

Compare agents on same scenarios to understand expected differences:

```python
comparison = compare_agents(spark, test_scenarios)
metrics = compute_agent_metrics_from_comparison(comparison)

print(f"Agreement Rate: {metrics['agreement_rate']:.1%}")
print(f"Llama Latency Overhead: {metrics['llama_agent']['avg_latency_ms'] - metrics['rule_agent']['avg_latency_ms']:.1f}ms")
```

**Goal:** Quantify expected agreement rate and latency before A/B test.

---

### 3. LLM Prompt Iteration

Test prompt changes and measure impact:

```python
# Baseline prompt
agent_v1 = LlamaSupplyChainAgent(temperature=0.1)
comparison_v1 = compare_agents(spark, scenarios, llama_agent=agent_v1)

# Updated prompt
agent_v2 = LlamaSupplyChainAgent(temperature=0.05)  # More deterministic
comparison_v2 = compare_agents(spark, scenarios, llama_agent=agent_v2)

# Compare
print(f"V1 Agreement: {comparison_v1.get_agreement_rate():.1%}")
print(f"V2 Agreement: {comparison_v2.get_agreement_rate():.1%}")
```

**Goal:** Improve LLM consistency and alignment with business rules.

---

### 4. Value-Add Analysis

Identify where LLM provides better decisions than rules:

```python
disagreements = compare_agent_differences(comparison)

# Manual review: For each disagreement, determine which agent was correct
for example in disagreements['examples']:
    print(f"Rule: {example['rule_action']} - {example['rule_reasoning']}")
    print(f"Llama: {example['llama_action']} - {example['llama_reasoning']}")
    # Human judgment: Which is better?
```

**Goal:** Quantify % of cases where LLM adds business value.

---

### 5. Hybrid Agent Design

Use disagreement patterns to design hybrid agent:

```python
class HybridAgent(BaseSupplyChainAgent):
    def decide(self, context):
        # Use rules for clear-cut cases
        if context['inventory_risk']['projected_days_to_stockout'] < 7:
            return self.rule_agent.decide(context)
        
        # Use LLM for nuanced cases
        if context['supplier_risk']['risk_level'] in ['MEDIUM', 'HIGH']:
            return self.llama_agent.decide(context)
        
        # Default to rules
        return self.rule_agent.decide(context)
```

**Goal:** Best of both worlds - speed of rules + nuance of LLM.

---

## Running Tests

### Full Comparison Test

```bash
%run /Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/tests/test_agent_comparison.py
```

**Output:**
- Comparison summary
- Side-by-side table
- Performance metrics
- Disagreement analysis
- Key insights

---

## Production Integration

### 1. Log Comparison Results

```python
# After comparison
for scenario in comparison.scenarios:
    spark.sql(f"""
    INSERT INTO agentdb.silver.agent_comparison_log
    VALUES (
        '{scenario['scenario']['product_key']}',
        '{scenario['scenario']['store_key']}',
        '{scenario['rule_decision']['action']}',
        '{scenario['llama_decision']['action']}',
        {scenario['agreement']},
        CURRENT_TIMESTAMP()
    )
    """)
```

### 2. Monitor Agreement Rate Over Time

```python
query = """
SELECT
    DATE_TRUNC('day', comparison_timestamp) as date,
    COUNT(*) as total_comparisons,
    SUM(CASE WHEN agreement = true THEN 1 ELSE 0 END) as agreements,
    AVG(CASE WHEN agreement = true THEN 1.0 ELSE 0.0 END) as agreement_rate
FROM agentdb.silver.agent_comparison_log
GROUP BY date
ORDER BY date DESC
LIMIT 30
"""

spark.sql(query).display()
```

### 3. Alert on Low Agreement

```python
recent_agreement_rate = ...  # Compute from logs

if recent_agreement_rate < 0.7:
    send_alert(
        "LLM agreement rate dropped below 70%",
        "Investigate prompt drift or data distribution shift"
    )
```

---

## Best Practices

### 1. Test on Representative Scenarios

- ✅ Include edge cases (stockouts, supplier failures, healthy inventory)
- ✅ Cover full range of risk levels (LOW, MEDIUM, HIGH, CRITICAL)
- ✅ Test with missing data (empty forecasts, no recommendations)

### 2. Measure What Matters

- **Agreement rate** - High = LLM learned rules well
- **Latency** - Critical for production performance
- **Explanation quality** - Why is reasoning better?
- **Business impact** - Does LLM reduce stockouts?

### 3. Iterate on Disagreements

- **Review manually** - Which agent was correct?
- **Update rules** - If LLM catches pattern rules missed
- **Improve prompt** - If LLM makes wrong decisions
- **Add hybrid logic** - Use LLM only where it adds value

### 4. Track Metrics Over Time

- Monitor agreement rate trends
- Alert on degradation
- A/B test changes before full rollout

---

## Files

- `comparison_framework.py` - Core comparison logic
- `metrics_tracker.py` - Metrics computation
- `../tests/test_agent_comparison.py` - Comprehensive test
- `README.md` - This file
