"""TEST: Hybrid Agent Routing Logic (V1.0 Enhanced)

Demonstrates the Hybrid Agent's intelligent routing with V1.0 improvements:
1. ✅ Complexity scoring (not binary routing)
2. ✅ Clear LLM failure tracking (not pretending LLM decided)
3. ✅ Decision explanation layer (rich provenance)

The hybrid agent uses:
- RULES for low complexity cases (complexity score < threshold)
- LLM for high complexity cases (complexity score >= threshold)

This test shows:
1. Complexity scoring function
2. Engine routing based on score
3. LLM failure handling (explicit fallback)
4. Decision explanation with full provenance

Usage:
    %run /Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/tests/test_hybrid_agent.py
"""

import sys
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

from decision.hybrid_agent import HybridAgent
from decision.rule_based_agent import RuleBasedAgent
from decision.llama_agent import LlamaSupplyChainAgent
from evaluation.decision_explanation import (
    create_decision_explanation,
    print_decision_explanation
)

print("="*80)
print("HYBRID AGENT ROUTING TEST (V1.0 ENHANCED)")
print("="*80)

# ============================================================================
# Test Cases: Complexity Scoring
# ============================================================================

test_cases = [
    {
        "name": "LOW risk inventory, healthy supplier (LOW complexity)",
        "expected_complexity": "low",
        "context": {
            "inventory_risk": {
                "risk_level": "LOW",
                "projected_days_to_stockout": 30,
                "inventory_qty": 500,
                "forecast_7d": 50
            },
            "supplier_risk": {
                "risk_level": "LOW",
                "on_time_delivery_rate": 95,
                "quality_score": 4.5
            },
            "forecast": {"forecast_7d": 50, "forecast_14d": 100, "forecast_30d": 200},
            "purchase_orders": {"open_po_count": 0},
            "recommendation": {},
            "recommendation_history": [],
            "previous_outcome": None
        }
    },
    {
        "name": "CRITICAL inventory risk (HIGH complexity)",
        "expected_complexity": "high",
        "context": {
            "inventory_risk": {
                "risk_level": "CRITICAL",
                "projected_days_to_stockout": 3,
                "inventory_qty": 20,
                "forecast_7d": 50
            },
            "supplier_risk": {
                "risk_level": "LOW",
                "on_time_delivery_rate": 95,
                "quality_score": 4.5
            },
            "forecast": {"forecast_7d": 50, "forecast_14d": 100, "forecast_30d": 200},
            "purchase_orders": {"open_po_count": 1},
            "recommendation": {},
            "recommendation_history": [],
            "previous_outcome": None
        }
    },
    {
        "name": "CRITICAL supplier risk (HIGH complexity)",
        "expected_complexity": "high",
        "context": {
            "inventory_risk": {
                "risk_level": "MEDIUM",
                "projected_days_to_stockout": 15,
                "inventory_qty": 200,
                "forecast_7d": 50
            },
            "supplier_risk": {
                "risk_level": "CRITICAL",
                "on_time_delivery_rate": 60,
                "quality_score": 2.0
            },
            "forecast": {"forecast_7d": 50, "forecast_14d": 100, "forecast_30d": 200},
            "purchase_orders": {"open_po_count": 0},
            "recommendation": {},
            "recommendation_history": [],
            "previous_outcome": None
        }
    },
    {
        "name": "Repeated recommendations (HIGH complexity)",
        "expected_complexity": "high",
        "context": {
            "inventory_risk": {
                "risk_level": "MEDIUM",
                "projected_days_to_stockout": 12,
                "inventory_qty": 100,
                "forecast_7d": 50
            },
            "supplier_risk": {
                "risk_level": "LOW",
                "on_time_delivery_rate": 90,
                "quality_score": 4.0
            },
            "forecast": {"forecast_7d": 50, "forecast_14d": 100, "forecast_30d": 200},
            "purchase_orders": {"open_po_count": 1},
            "recommendation": {"action": "REORDER"},
            "recommendation_history": [
                {"action": "REORDER", "reasoning": "...", "status": "PENDING"},
                {"action": "REORDER", "reasoning": "...", "status": "PENDING"},
                {"action": "REORDER", "reasoning": "...", "status": "PENDING"}
            ],
            "previous_outcome": "PENDING"
        }
    },
    {
        "name": "Conflicting signals (HIGH complexity)",
        "expected_complexity": "high",
        "context": {
            "inventory_risk": {
                "risk_level": "HIGH",
                "projected_days_to_stockout": 8,
                "inventory_qty": 50,
                "forecast_7d": 50
            },
            "supplier_risk": {
                "risk_level": "HIGH",
                "on_time_delivery_rate": 70,
                "quality_score": 3.0
            },
            "forecast": {"forecast_7d": 50, "forecast_14d": 100, "forecast_30d": 200},
            "purchase_orders": {"open_po_count": 0},
            "recommendation": {},
            "recommendation_history": [],
            "previous_outcome": None
        }
    }
]

# ============================================================================
# Run Tests
# ============================================================================

print("\nRunning test cases...")
print("="*80)

# Initialize hybrid agent with default threshold (3.0)
hybrid_agent = HybridAgent(complexity_threshold=3.0)
results = []

for i, test_case in enumerate(test_cases, 1):
    print(f"\nTest Case {i}: {test_case['name']}")
    print("-" * 80)
    
    # Make decision
    decision = hybrid_agent.decide(test_case['context'])
    
    # Get decision details
    complexity_score = decision.get('complexity_score', 0)
    decision_engine = decision.get('decision_engine', 'unknown')
    engine_status = decision.get('engine_status', 'unknown')
    
    # Create decision explanation (V1.0 NEW!)
    explanation = create_decision_explanation(
        decision=decision,
        context=test_case['context'],
        tools_used=["get_inventory_risk", "get_supplier_risk", "get_forecast", "get_purchase_orders"],
        agent_version="1.0.0"
    )
    
    result = {
        "name": test_case['name'],
        "complexity_score": complexity_score,
        "decision_engine": decision_engine,
        "engine_status": engine_status,
        "decision": decision,
        "explanation": explanation
    }
    results.append(result)
    
    # Print result
    print(f"Complexity Score: {complexity_score:.2f}")
    print(f"Decision Engine:  {decision_engine.upper()}")
    print(f"Engine Status:    {engine_status}")
    
    # Show fallback info if applicable
    if decision_engine == "rule_fallback":
        print(f"Fallback Reason:  {decision.get('fallback_reason', 'N/A')}")
        print(f"Attempted Engine: {decision.get('attempted_engine', 'N/A')}")
        print("→ LLM FAILED, using rule engine as fallback (safety)")
    
    print(f"\nDecision:")
    print(f"  Action:     {decision['action']}")
    print(f"  Priority:   {decision['priority']}")
    print(f"  Confidence: {decision['confidence']:.2f}")
    print(f"  Reasoning:  {decision['reasoning'][:80]}...")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*80)
print("ROUTING SUMMARY")
print("="*80)

total_tests = len(results)
rule_decisions = sum(1 for r in results if r['decision_engine'] == 'rule')
llama_decisions = sum(1 for r in results if r['decision_engine'] == 'llama')
fallback_decisions = sum(1 for r in results if r['decision_engine'] == 'rule_fallback')

avg_complexity = sum(r['complexity_score'] for r in results) / total_tests

print(f"\nTotal Tests: {total_tests}")
print(f"Average Complexity Score: {avg_complexity:.2f}")
print(f"\nEngine Usage:")
print(f"  Rule Engine:      {rule_decisions} ({rule_decisions/total_tests*100:.0f}%)")
print(f"  LLM Engine:       {llama_decisions} ({llama_decisions/total_tests*100:.0f}%)")
print(f"  Rule Fallback:    {fallback_decisions} ({fallback_decisions/total_tests*100:.0f}%)")

if fallback_decisions > 0:
    print(f"\n⚠ FALLBACK ALERT: {fallback_decisions} LLM failures detected")
    print("→ These are NOT LLM decisions, they are rule fallbacks")
    print("→ Review LLM endpoint availability and validation logic")

print("\n" + "="*80)
print("COMPLEXITY SCORING BREAKDOWN")
print("="*80)

print("\nComplexity Score Components:")
print("  +3.0  = Imminent stockout (< 7 days)")
print("  +1.5  = Stockout within 14 days")
print("  +2.0  = CRITICAL inventory risk")
print("  +1.0  = HIGH inventory risk")
print("  +2.0  = CRITICAL supplier risk")
print("  +1.0  = HIGH supplier risk")
print("  +2.0  = Repeated recommendations (not working)")
print("  +1.5  = Conflicting signals (both risks high)")
print("  +0.5  = Multiple open POs (≥3)")
print("  +1.0  = High forecast uncertainty (>30%)")
print(f"\nThreshold: {hybrid_agent.complexity_threshold:.1f}")
print("  Score < 3.0 → Rule Engine")
print("  Score ≥ 3.0 → LLM Engine")

# Show complexity scores
print("\nTest Case Complexity Scores:")
for r in results:
    print(f"  {r['name'][:50]:50} | Score: {r['complexity_score']:.2f} | Engine: {r['decision_engine'].upper()}")

print("\n" + "="*80)
print("DECISION EXPLANATION EXAMPLE")
print("="*80)

# Print detailed explanation for first complex case
complex_cases = [r for r in results if r['complexity_score'] >= 3.0]
if complex_cases:
    print(f"\nShowing detailed explanation for: {complex_cases[0]['name']}")
    print_decision_explanation(complex_cases[0]['explanation'])

print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)

print("""
1. COMPLEXITY SCORING (V1.0 Improvement)
   ✓ Extensible scoring function (not binary rules)
   ✓ Easy to add new complexity factors
   ✓ Tunable threshold for production
   
2. LLM FAILURE TRACKING (V1.0 Improvement)
   ✓ Clear distinction: LLM success vs LLM failure
   ✓ Fallback decisions clearly marked as "rule_fallback"
   ✓ Fallback reason captured for debugging
   ✓ Metrics show TRUE LLM usage, not inflated by fallbacks
   
3. DECISION EXPLANATION (V1.0 Improvement)
   ✓ Rich provenance for every decision
   ✓ Tools used, facts extracted, reasoning captured
   ✓ Version tracking for reproducibility
   ✓ Audit trail for compliance
   
4. COST OPTIMIZATION
   If 70% of production scenarios have complexity < 3.0:
   - 70% use rule engine (free, <10ms)
   - 30% use LLM engine (API cost, ~800ms)
   - Average latency: 0.7*10 + 0.3*800 = 247ms
   - vs pure LLM: 800ms (3.2x faster!)
   - API cost reduction: 70%
   
5. PRODUCTION STRATEGY
   - Tune complexity threshold based on real data
   - Monitor fallback rate (should be < 5%)
   - Log all decisions with explanations
   - Review complex cases monthly
   - Adjust scoring weights as patterns emerge
""")

print("="*80)
print("TEST COMPLETE")
print("="*80)

print("""
V1.0 IMPROVEMENTS DEMONSTRATED:

✅ 1. Complexity Scoring Function
   - Extensible, tunable, explainable
   - Not binary (LOW → rule, else → LLM)
   - Easy to add new factors

✅ 2. LLM Failure Tracking
   - Engine status: SUCCESS or FAILED
   - Fallback clearly marked as "rule_fallback"
   - Fallback reason captured
   - Honest metrics (not pretending LLM decided)

✅ 3. Decision Explanation Layer
   - Decision source, version, timestamp
   - Tools used, facts extracted
   - Full provenance for audit trail
   - Reproducibility for debugging

NEXT STEPS:

1. Run on production data
2. Tune complexity threshold (try 2.5, 3.0, 3.5)
3. Analyze fallback reasons
4. Store decision explanations in database
5. Build dashboard showing:
   - Engine usage over time
   - Complexity distribution
   - Fallback rate
   - Decision patterns
""")
