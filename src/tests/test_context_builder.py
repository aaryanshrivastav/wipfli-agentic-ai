"""TEST 4: Context Builder Test

Tests build_agent_context() function which assembles tool outputs into a context dict.

Expected Behavior:
1. Takes 5 tool outputs as input
2. Returns a dict with keys: inventory_risk, supplier_risk, forecast, recommendation, purchase_orders
3. All 5 keys must be present

Depends on:
- TEST 1: Tool outputs available (4A)
"""

import sys
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

from orchestrator.context_builder import build_agent_context

# TEST EXECUTION
print("="*60)
print("TEST 4: CONTEXT BUILDER")
print("="*60)

try:
    print("\nStep 1: Creating mock tool outputs...")
    
    # Mock tool outputs (matching actual tool return structures)
    inventory_risk = {
        "product_key": 1,
        "store_key": 1,
        "inventory_qty": 100,
        "risk_level": "HIGH",
        "forecast_7d": 50,
        "forecast_14d": 100,
        "forecast_30d": 200,
        "projected_days_to_stockout": 2
    }
    
    supplier_risk = {
        "supplier_key": 1,
        "risk_level": "LOW",
        "on_time_delivery_rate": 0.95
    }
    
    forecast = {
        "forecast_7d": 50,
        "forecast_14d": 100,
        "forecast_30d": 200
    }
    
    recommendation = {
        "product_key": 1,
        "store_key": 1,
        "recommendation_type": "REORDER",
        "generated_at": "2026-06-24T12:00:00"
    }
    
    purchase_orders = {
        "open_po_count": 3
    }
    
    print("✓ Mock outputs created")
    
    print("\nStep 2: Building agent context...")
    context = build_agent_context(
        inventory_risk=inventory_risk,
        supplier_risk=supplier_risk,
        forecast=forecast,
        recommendation=recommendation,
        purchase_orders=purchase_orders
    )
    
    print("✓ Context built successfully")
    
    print("\nStep 3: Verifying context structure...")
    print("-" * 60)
    
    expected_keys = [
        'inventory_risk',
        'supplier_risk',
        'forecast',
        'recommendation',
        'purchase_orders'
    ]
    
    all_present = True
    for key in expected_keys:
        if key in context:
            print(f"  ✓ {key}: Present")
        else:
            print(f"  ✗ {key}: MISSING")
            all_present = False
    
    print("\nStep 4: Verifying context contents...")
    print("-" * 60)
    
    # Verify data integrity
    checks = [
        ('inventory_risk matches', context['inventory_risk'] == inventory_risk),
        ('supplier_risk matches', context['supplier_risk'] == supplier_risk),
        ('forecast matches', context['forecast'] == forecast),
        ('recommendation matches', context['recommendation'] == recommendation),
        ('purchase_orders matches', context['purchase_orders'] == purchase_orders)
    ]
    
    for check_name, passed in checks:
        print(f"  {'✓' if passed else '✗'} {check_name}")
    
    all_passed = all_present and all(check[1] for check in checks)
    
    print("\n" + "="*60)
    print("TEST 4: PASS" if all_passed else "TEST 4: FAIL")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 4 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
