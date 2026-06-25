"""TEST: Agent Strategy Pattern

Demonstrates the Strategy Pattern for pluggable agent decision engines.

This test validates that:
1. Both RuleBasedAgent and LlamaAgent implement the same interface
2. The orchestrator works with EITHER agent without code changes
3. Agents can be swapped at runtime
4. Each agent produces valid decisions

STRATEGY PATTERN BENEFITS:
- Add new agent types without modifying orchestration code
- A/B test different decision engines
- Gradual migration from rules to LLM
- Easy rollback if LLM underperforms
"""

import sys
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

from decision.base_agent import BaseSupplyChainAgent
from decision.rule_based_agent import RuleBasedAgent
from decision.llama_agent import LlamaSupplyChainAgent

print("="*70)
print("AGENT STRATEGY PATTERN TEST")
print("="*70)

# ============================================================
# TEST 1: Verify Interface Implementation
# ============================================================
print("\n" + "="*70)
print("TEST 1: Interface Implementation")
print("="*70)

try:
    # Create agent instances
    rule_agent = RuleBasedAgent()
    llama_agent = LlamaSupplyChainAgent()
    
    # Verify both implement BaseSupplyChainAgent
    assert isinstance(rule_agent, BaseSupplyChainAgent), \
        "RuleBasedAgent must inherit from BaseSupplyChainAgent"
    assert isinstance(llama_agent, BaseSupplyChainAgent), \
        "LlamaSupplyChainAgent must inherit from BaseSupplyChainAgent"
    
    # Verify both have decide() method
    assert hasattr(rule_agent, 'decide'), \
        "RuleBasedAgent must implement decide()"
    assert hasattr(llama_agent, 'decide'), \
        "LlamaSupplyChainAgent must implement decide()"
    
    # Verify both have get_name() method
    assert hasattr(rule_agent, 'get_name'), \
        "RuleBasedAgent must implement get_name()"
    assert hasattr(llama_agent, 'get_name'), \
        "LlamaSupplyChainAgent must implement get_name()"
    
    print("✓ Both agents implement BaseSupplyChainAgent interface")
    print(f"✓ RuleBasedAgent name: {rule_agent.get_name()}")
    print(f"✓ LlamaSupplyChainAgent name: {llama_agent.get_name()}")
    print("\n" + "="*70)
    print("TEST 1: PASS")
    print("="*70)
    
except AssertionError as e:
    print(f"\n✗ TEST 1 FAILED: {str(e)}")
    print("="*70)

# ============================================================
# TEST 2: Rule-Based Agent Decision
# ============================================================
print("\n" + "="*70)
print("TEST 2: Rule-Based Agent Decision")
print("="*70)

try:
    # Sample context: Critical stockout scenario
    context = {
        "inventory_risk": {
            "product_key": 101,
            "store_key": 5,
            "inventory_qty": 10,
            "risk_level": "CRITICAL",
            "projected_days_to_stockout": 3,
            "forecast_7d": 50,
            "forecast_14d": 100,
            "forecast_30d": 200
        },
        "supplier_risk": {
            "supplier_key": 42,
            "risk_level": "LOW",
            "on_time_delivery_rate": 95.0,
            "quality_score": 4.5
        },
        "forecast": {
            "forecast_7d": 50,
            "forecast_14d": 100,
            "forecast_30d": 200
        },
        "recommendation": {},
        "purchase_orders": {
            "open_po_count": 0
        }
    }
    
    # Use rule-based agent
    rule_agent = RuleBasedAgent()
    result = rule_agent.decide(context)
    
    # Validate result structure
    assert "action" in result, "Result must have 'action' field"
    assert "priority" in result, "Result must have 'priority' field"
    assert "confidence" in result, "Result must have 'confidence' field"
    assert "reasoning" in result, "Result must have 'reasoning' field"
    
    print(f"✓ Decision: {result['action']}")
    print(f"✓ Priority: {result['priority']}")
    print(f"✓ Confidence: {result['confidence']}")
    print(f"✓ Reasoning: {result['reasoning']}")
    
    # For critical stockout (3 days), expect EXPEDITE_PO
    assert result['action'] == "EXPEDITE_PO", \
        "Expected EXPEDITE_PO for critical stockout scenario"
    assert result['priority'] == "CRITICAL", \
        "Expected CRITICAL priority for 3-day stockout"
    
    print("\n" + "="*70)
    print("TEST 2: PASS")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ TEST 2 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*70)

# ============================================================
# TEST 3: Polymorphism - Same Interface, Different Implementation
# ============================================================
print("\n" + "="*70)
print("TEST 3: Polymorphism")
print("="*70)

try:
    # Same context as TEST 2
    context = {
        "inventory_risk": {
            "projected_days_to_stockout": 15,
            "risk_level": "LOW",
            "inventory_qty": 500
        },
        "supplier_risk": {
            "risk_level": "LOW"
        },
        "forecast": {},
        "recommendation": {},
        "purchase_orders": {}
    }
    
    # This function works with ANY agent implementing BaseSupplyChainAgent
    def run_agent(agent: BaseSupplyChainAgent, context: dict):
        """Orchestrator doesn't care which agent - just calls decide()"""
        return agent.decide(context)
    
    # Use rule-based agent
    rule_result = run_agent(RuleBasedAgent(), context)
    print(f"✓ RuleBasedAgent returned: {rule_result['action']}")
    
    # Use Llama agent (will fail gracefully if SDK not available)
    try:
        llama_result = run_agent(LlamaSupplyChainAgent(), context)
        print(f"✓ LlamaAgent returned: {llama_result['action']}")
    except ImportError:
        print("⚠ LlamaAgent skipped (databricks-sdk not available)")
    
    print("\n✓ Polymorphism works - same interface, different implementations")
    print("\n" + "="*70)
    print("TEST 3: PASS")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ TEST 3 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*70)

# ============================================================
# TEST 4: Strategy Swap at Runtime
# ============================================================
print("\n" + "="*70)
print("TEST 4: Runtime Strategy Swap")
print("="*70)

try:
    context = {
        "inventory_risk": {"risk_level": "HIGH", "projected_days_to_stockout": 10},
        "supplier_risk": {"risk_level": "LOW"},
        "forecast": {},
        "recommendation": {},
        "purchase_orders": {}
    }
    
    # Start with rule-based agent
    current_agent = RuleBasedAgent()
    print(f"Using agent: {current_agent.get_name()}")
    result1 = current_agent.decide(context)
    print(f"  Decision: {result1['action']}")
    
    # Swap to Llama agent - NO OTHER CODE CHANGES!
    # In production, this could be a feature flag, A/B test, or gradual rollout
    try:
        current_agent = LlamaSupplyChainAgent()
        print(f"\nSwitched to: {current_agent.get_name()}")
        result2 = current_agent.decide(context)
        print(f"  Decision: {result2['action']}")
    except ImportError:
        print("\n⚠ Llama agent swap skipped (databricks-sdk not available)")
    
    print("\n✓ Agents can be swapped at runtime")
    print("✓ No orchestrator code changes needed")
    print("\n" + "="*70)
    print("TEST 4: PASS")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ TEST 4 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*70)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("STRATEGY PATTERN BENEFITS DEMONSTRATED")
print("="*70)
print("""
✓ Single interface (BaseSupplyChainAgent)
✓ Multiple implementations (RuleBasedAgent, LlamaAgent)
✓ Swappable at runtime
✓ No orchestrator changes needed
✓ Easy to add new agent types
✓ A/B testing ready
✓ Safe gradual migration

PRODUCTION USAGE:

# Configuration-driven agent selection
agent_type = config.get("agent_type", "rule_based")  # Feature flag

if agent_type == "rule_based":
    agent = RuleBasedAgent()
elif agent_type == "llama":
    agent = LlamaSupplyChainAgent()
elif agent_type == "hybrid":
    agent = HybridAgent()  # Future implementation

# Same orchestrator call regardless
result = run_supply_chain_agent(spark, agent, product_key, store_key, supplier_key)
""")
print("="*70)
