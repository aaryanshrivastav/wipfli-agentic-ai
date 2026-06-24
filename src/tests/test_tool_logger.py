"""TEST 2B: Tool Logger Test

Tests agent_tool_execution_log table functionality.

Table Schema:
- tool_execution_id (auto-increment), run_id, tool_name
- entity_type, entity_id
- execution_start_timestamp, execution_end_timestamp
- execution_duration_ms, success_flag, error_message
- created_at

Expected Behavior:
1. Insert a tool execution record
2. Verify data in agentdb.silver.agent_tool_execution_log
"""

import uuid
from datetime import datetime

# TEST EXECUTION
print("="*60)
print("TEST 2B: TOOL LOGGER")
print("="*60)

try:
    # Generate a unique run_id
    run_id = str(uuid.uuid4())
    print(f"\n✓ Generated run_id: {run_id}")
    
    # Prepare test data
    tool_name = "get_inventory_risk"
    entity_type = "inventory"
    entity_id = 1
    execution_duration_ms = 150.0
    
    print(f"\nStep 1: Logging tool execution...")
    print(f"  Tool: {tool_name}")
    print(f"  Entity: {entity_type} (ID: {entity_id})")
    print(f"  Execution time: {execution_duration_ms}ms")
    
    # Insert tool execution log
    insert_query = f"""
    INSERT INTO agentdb.silver.agent_tool_execution_log
    (
        run_id,
        tool_name,
        entity_type,
        entity_id,
        execution_start_timestamp,
        execution_end_timestamp,
        execution_duration_ms,
        success_flag,
        error_message,
        created_at
    )
    VALUES
    (
        '{run_id}',
        '{tool_name}',
        '{entity_type}',
        {entity_id},
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        {execution_duration_ms},
        true,
        NULL,
        CURRENT_TIMESTAMP()
    )
    """
    
    spark.sql(insert_query)
    print("\n✓ INSERT successful")
    
    # Step 2: Verify data in table
    print("\nStep 2: Verifying data in agent_tool_execution_log...")
    verify_query = f"""
    SELECT *
    FROM agentdb.silver.agent_tool_execution_log
    WHERE run_id = '{run_id}'
    """
    
    result_df = spark.sql(verify_query)
    result = result_df.first()
    
    if result:
        print("\n✓ Record found in agent_tool_execution_log:")
        print("-" * 60)
        print(f"  tool_execution_id: {result['tool_execution_id']}")
        print(f"  run_id: {result['run_id']}")
        print(f"  tool_name: {result['tool_name']}")
        print(f"  entity_type: {result['entity_type']}")
        print(f"  entity_id: {result['entity_id']}")
        print(f"  execution_duration_ms: {result['execution_duration_ms']}")
        print(f"  success_flag: {result['success_flag']}")
        print(f"  created_at: {result['created_at']}")
        
        # Check fields
        checks = [
            ('run_id', result['run_id'] == run_id),
            ('tool_name', result['tool_name'] == tool_name),
            ('entity_type', result['entity_type'] == entity_type),
            ('entity_id', result['entity_id'] == entity_id),
            ('execution_duration_ms', result['execution_duration_ms'] == execution_duration_ms),
            ('success_flag', result['success_flag'] == True),
            ('created_at', result['created_at'] is not None)
        ]
        
        print("\n" + "-" * 60)
        for field, passed in checks:
            print(f"  {'✓' if passed else '✗'} {field}")
        
        all_passed = all(check[1] for check in checks)
        
        print("\n" + "="*60)
        print("TEST 2B: PASS" if all_passed else "TEST 2B: FAIL")
        print("="*60)
    else:
        print("\n✗ No record found in agent_tool_execution_log")
        print("="*60)
        print("TEST 2B: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 2B FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
