"""TEST 6: Output Validator Test

Tests validate_agent_output() function which validates agent decision structure.

Expected Behavior:
1. Validates required fields: action, priority, confidence, reasoning
2. Validates action is in VALID_ACTIONS set
3. Raises exception if validation fails
4. Returns True if validation passes

Valid Actions:
- REORDER
- EXPEDITE_PO
- SUPPLIER_ALERT
- NO_ACTION

Depends on:
- TEST 5: Agent output structure
"""

import sys
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

from orchestrator.output_validator import validate_agent_output, VALID_ACTIONS

# TEST EXECUTION
print("="*60)
print("TEST 6: OUTPUT VALIDATOR")
print("="*60)

print(f"\nValid Actions: {VALID_ACTIONS}")
print("")

# Test cases
test_cases = []

# TEST 6.1: Valid output
test_cases.append({
    "name": "Valid output - REORDER",
    "output": {
        "action": "REORDER",
        "priority": "HIGH",
        "confidence": 0.88,
        "reasoning": "Inventory risk requires reorder."
    },
    "should_pass": True
})

# TEST 6.2: Valid output - EXPEDITE_PO
test_cases.append({
    "name": "Valid output - EXPEDITE_PO",
    "output": {
        "action": "EXPEDITE_PO",
        "priority": "CRITICAL",
        "confidence": 0.95,
        "reasoning": "Stockout imminent."
    },
    "should_pass": True
})

# TEST 6.3: Missing field
test_cases.append({
    "name": "Missing field - no confidence",
    "output": {
        "action": "REORDER",
        "priority": "HIGH",
        "reasoning": "Test"
    },
    "should_pass": False
})

# TEST 6.4: Invalid action
test_cases.append({
    "name": "Invalid action",
    "output": {
        "action": "CANCEL_ORDER",  # Not in VALID_ACTIONS
        "priority": "HIGH",
        "confidence": 0.90,
        "reasoning": "Test"
    },
    "should_pass": False
})

# TEST 6.5: Valid output - NO_ACTION
test_cases.append({
    "name": "Valid output - NO_ACTION",
    "output": {
        "action": "NO_ACTION",
        "priority": "LOW",
        "confidence": 0.99,
        "reasoning": "Inventory healthy."
    },
    "should_pass": True
})

# TEST 6.6: Valid output - SUPPLIER_ALERT
test_cases.append({
    "name": "Valid output - SUPPLIER_ALERT",
    "output": {
        "action": "SUPPLIER_ALERT",
        "priority": "HIGH",
        "confidence": 0.90,
        "reasoning": "Supplier risk high."
    },
    "should_pass": True
})

# Run test cases
try:
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{'-'*60}")
        print(f"TEST 6.{i}: {test_case['name']}")
        print("-"*60)
        
        try:
            result = validate_agent_output(test_case['output'])
            
            if test_case['should_pass']:
                print(f"  ✓ Validation passed (as expected)")
                print(f"  ✓ TEST 6.{i}: PASS")
                passed += 1
            else:
                print(f"  ✗ Validation passed but should have failed")
                print(f"  ✗ TEST 6.{i}: FAIL")
                failed += 1
                
        except Exception as e:
            if not test_case['should_pass']:
                print(f"  ✓ Validation failed with: {str(e)} (as expected)")
                print(f"  ✓ TEST 6.{i}: PASS")
                passed += 1
            else:
                print(f"  ✗ Validation failed unexpectedly: {str(e)}")
                print(f"  ✗ TEST 6.{i}: FAIL")
                failed += 1
    
    print("\n" + "="*60)
    print(f"TEST 6 SUMMARY: {passed}/{len(test_cases)} test cases passed")
    if passed == len(test_cases):
        print("TEST 6: PASS")
    else:
        print("TEST 6: FAIL")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 6 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
