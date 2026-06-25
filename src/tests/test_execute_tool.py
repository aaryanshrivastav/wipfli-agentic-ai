"""TEST 3: Tool Wrapper Integration Test

Tests execute_tool() function which wraps tool execution with logging.

This validates that:
1. Tools execute successfully
2. Results are returned
3. Execution is logged to agent_tool_execution_log

Depends on:
- TEST 1: Tools working (4A)
- TEST 2: Memory layer working (4B)
"""

import uuid
import sys
sys.path.append('/Workspace/Users/aaryan.shrivastav1403@gmail.com/wipfli-agentic-ai/src/agents')

# Clear any cached imports to ensure we get the updated tool files
import importlib
if 'tools.inventory_tools' in sys.modules:
    importlib.reload(sys.modules['tools.inventory_tools'])
if 'services.memory_services' in sys.modules:
    importlib.reload(sys.modules['services.memory_services'])

# Import memory service and tool
from services.memory_services import execute_tool
from tools.inventory_tools import get_inventory_risk

# TEST EXECUTION
print("="*60)
print("TEST 3: TOOL WRAPPER (execute_tool)")
print("="*60)

try:
    # Generate a run_id
    run_id = str(uuid.uuid4())
    print(f"\n✓ Generated run_id: {run_id}")
    
    print("\nStep 1: Getting sample data to test with...")
    
    # Get sample product/store from inventory_risk table
    sample_query = """
    SELECT product_key, store_key
    FROM agentdb.intelligence.inventory_risk
    LIMIT 1
    """
    sample = spark.sql(sample_query).first()
    
    if not sample:
        print("\n⚠ WARNING: No data in inventory_risk table")
        print("Cannot test execute_tool without data.")
        print("="*60)
    else:
        product_key = sample['product_key']
        store_key = sample['store_key']
        
        print(f"  Testing with product_key={product_key}, store_key={store_key}")
        
        print("\nStep 2: Testing tool directly (pass spark)...")
        
        # Call tool directly with Spark SQL
        result = get_inventory_risk(
            spark=spark,
            product_key=product_key,
            store_key=store_key
        )
        
        print(f"✓ Tool executed successfully")
        print(f"  Result keys: {list(result.keys())}")
        
        print("\nStep 3: Testing execute_tool wrapper...")
        
        # Call tool via execute_tool wrapper
        result2 = execute_tool(
            spark=spark,
            run_id=run_id,
            tool_name="get_inventory_risk",
            tool_function=get_inventory_risk,
            entity_type="inventory",
            entity_id=product_key,
            product_key=product_key,
            store_key=store_key
        )
        
        print(f"✓ execute_tool wrapper executed successfully")
        print(f"  Result keys: {list(result2.keys())}")
        
        print("\nStep 4: Verify tool execution logged...")
        
        # Check if execution was logged
        log_query = f"""
        SELECT *
        FROM agentdb.silver.agent_tool_execution_log
        WHERE run_id = '{run_id}'
        AND tool_name = 'get_inventory_risk'
        """
        log_record = spark.sql(log_query).first()
        
        if log_record:
            print(f"✓ Tool execution logged to agent_tool_execution_log")
            print(f"  Execution time: {log_record['execution_duration_ms']} ms")
        else:
            print(f"✗ Tool execution NOT logged")
        
        print("\n" + "="*60)
        print("TEST 3: PASS")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 3 FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
