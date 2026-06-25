"""TEST 5: Supply Chain Agent (Rule-Based) Test

Tests supply_chain_agent() function with 4 scenarios.

The agent uses rule-based logic:
1. If stockout < 7 days → EXPEDITE_PO (CRITICAL)
2. Else if supplier risk HIGH/CRITICAL → SUPPLIER_ALERT (HIGH)
3. Else if inventory risk HIGH/CRITICAL → REORDER (HIGH)
4. Else → NO_ACTION (LOW)

Expected Output Structure:
{
    "action": "...",
    "priority": "...",
    "confidence": float,
    "reasoning": "..."
}

Depends on:
- TEST 4: Context builder working
"""

import sys
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

from orchestrator.supply_chain_agent import supply_chain_agent

# TEST EXECUTION
print("="*60)
print("TEST 5: SUPPLY CHAIN AGENT (RULE AGENT)")
print("="*60)

# Define test scenarios
scenarios = []

# SCENARIO A: Stockout in < 7 days
scenarios.append({
    "name": "Scenario A: Stockout in 5 days",
    "context": {
        "inventory_risk": {
            "product_key": 1,
            "store_key": 1,
            "inventory_qty": 10,
            "risk_level": "CRITICAL",
            "projected_days_to_stockout": 5
        },
        "supplier_risk": {
            "supplier_key": 1,
            "risk_level": "LOW"
        },
        "forecast": {"forecast_7d": 50, "forecast_14d": 100, "forecast_30d": 200},
        "recommendation": {"recommendation_type": "EXPEDITE"},
        "purchase_orders": {"open_po_count": 1}
    },
    "expected_action": "EXPEDITE_PO",
    "expected_priority": "CRITICAL"
})

# SCENARIO B: Supplier risk HIGH
scenarios.append({
    "name": "Scenario B: Supplier risk HIGH",
    "context": {
        "inventory_risk": {
            "product_key": 1,
            "store_key": 1,
            "inventory_qty": 100,
            "risk_level": "LOW",
            "projected_days_to_stockout": 20
        },
        "supplier_risk": {
            "supplier_key": 1,
            "risk_level": "HIGH"
        },
        "forecast": {"forecast_7d": 10, "forecast_14d": 20, "forecast_30d": 50},
        "recommendation": {"recommendation_type": "ALERT"},
        "purchase_orders": {"open_po_count": 0}
    },
    "expected_action": "SUPPLIER_ALERT",
    "expected_priority": "HIGH"
})

# SCENARIO C: Inventory risk HIGH
scenarios.append({
    "name": "Scenario C: Inventory risk HIGH",
    "context": {
        "inventory_risk": {
            "product_key": 1,
            "store_key": 1,
            "inventory_qty": 20,
            "risk_level": "HIGH",
            "projected_days_to_stockout": 10
        },
        "supplier_risk": {
            "supplier_key": 1,
            "risk_level": "LOW"
        },
        "forecast": {"forecast_7d": 30, "forecast_14d": 60, "forecast_30d": 150},
        "recommendation": {"recommendation_type": "REORDER"},
        "purchase_orders": {"open_po_count": 0}
    },
    "expected_action": "REORDER",
    "expected_priority": "HIGH"
})

# SCENARIO D: Everything healthy
scenarios.append({
    "name": "Scenario D: Healthy inventory",
    "context": {
        "inventory_risk": {
            "product_key": 1,
            "store_key": 1,
            "inventory_qty": 500,
            "risk_level": "LOW",
            "projected_days_to_stockout": 45
        },
        "supplier_risk": {
            "supplier_key": 1,
            "risk_level": "LOW"
        },
        "forecast": {"forecast_7d": 20, "forecast_14d": 40, "forecast_30d": 100},
        "recommendation": {"recommendation_type": "NONE"},
        "purchase_orders": {"open_po_count": 0}
    },
    "expected_action": "NO_ACTION",
    "expected_priority": "LOW"
})

# Run all scenarios
try:
    passed_scenarios = 0
    failed_scenarios = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'-'*60}")
        print(f"TEST 5.{i}: {scenario['name']}")
        print("-"*60)
        
        try:
            result = supply_chain_agent(scenario['context'])
            
            print(f"  Result:")
            print(f"    Action: {result['action']}")
            print(f"    Priority: {result['priority']}")
            print(f"    Confidence: {result['confidence']}")
            print(f"    Reasoning: {result['reasoning']}")
            
            # Verify expected fields exist
            required_fields = ['action', 'priority', 'confidence', 'reasoning']
            fields_present = all(field in result for field in required_fields)
            
            # Verify expected values
            action_match = result['action'] == scenario['expected_action']
            priority_match = result['priority'] == scenario['expected_priority']
            
            if fields_present and action_match and priority_match:
                print(f"\n  ✓ TEST 5.{i}: PASS")
                passed_scenarios += 1
            else:
                print(f"\n  ✗ TEST 5.{i}: FAIL")
                if not action_match:
                    print(f"    Expected action: {scenario['expected_action']}, Got: {result['action']}")
                if not priority_match:
                    print(f"    Expected priority: {scenario['expected_priority']}, Got: {result['priority']}")
                failed_scenarios += 1
                
        except Exception as e:
            print(f"\n  ✗ TEST 5.{i}: EXCEPTION - {str(e)}")
            failed_scenarios += 1
    
    print("\n" + "="*60)
    print(f"TEST 5 SUMMARY: {passed_scenarios}/{len(scenarios)} scenarios passed")
    if passed_scenarios == len(scenarios):
        print("TEST 5: PASS")
    else:
        print("TEST 5: FAIL")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 5 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
