"""TEST 2A: Run Logger Test

Tests agent_run_log table functionality.

Table Schema:
- run_id, agent_name, trigger_type, run_timestamp
- execution_duration_ms, run_status, error_message
- recommendations_generated, recommendations_accepted, recommendations_rejected
- created_at

Expected Behavior:
1. Insert a new run record
2. Verify data in agentdb.silver.agent_run_log
"""

import uuid

# TEST EXECUTION
print("="*60)
print("TEST 2A: RUN LOGGER")
print("="*60)

try:
    # Generate a unique run_id
    run_id = str(uuid.uuid4())
    print(f"\n✓ Generated run_id: {run_id}")
    
    # Step 1: Create agent run (INSERT)
    print("\nStep 1: Creating agent run...")
    create_query = f"""
    INSERT INTO agentdb.silver.agent_run_log
    (
        run_id,
        agent_name,
        trigger_type,
        run_timestamp,
        execution_duration_ms,
        recommendations_generated,
        recommendations_accepted,
        recommendations_rejected,
        run_status,
        error_message,
        created_at
    )
    VALUES
    (
        '{run_id}',
        'supply_chain_agent',
        'test',
        CURRENT_TIMESTAMP(),
        150.5,
        1,
        1,
        0,
        'SUCCESS',
        NULL,
        CURRENT_TIMESTAMP()
    )
    """
    spark.sql(create_query)
    print("✓ INSERT successful")
    
    # Step 2: Verify data in table
    print("\nStep 2: Verifying data in agent_run_log...")
    verify_query = f"""
    SELECT *
    FROM agentdb.silver.agent_run_log
    WHERE run_id = '{run_id}'
    """
    
    result_df = spark.sql(verify_query)
    result = result_df.first()
    
    if result:
        print("\n✓ Record found in agent_run_log:")
        print("-" * 60)
        print(f"  run_id: {result['run_id']}")
        print(f"  agent_name: {result['agent_name']}")
        print(f"  trigger_type: {result['trigger_type']}")
        print(f"  run_status: {result['run_status']}")
        print(f"  run_timestamp: {result['run_timestamp']}")
        print(f"  execution_duration_ms: {result['execution_duration_ms']}")
        print(f"  recommendations_generated: {result['recommendations_generated']}")
        
        # Check fields
        checks = [
            ('run_id', result['run_id'] == run_id),
            ('agent_name', result['agent_name'] == 'supply_chain_agent'),
            ('run_status', result['run_status'] == 'SUCCESS'),
            ('run_timestamp', result['run_timestamp'] is not None),
            ('execution_duration_ms', result['execution_duration_ms'] == 150.5)
        ]
        
        print("\n" + "-" * 60)
        for field, passed in checks:
            print(f"  {'✓' if passed else '✗'} {field}")
        
        all_passed = all(check[1] for check in checks)
        
        print("\n" + "="*60)
        print("TEST 2A: PASS" if all_passed else "TEST 2A: FAIL")
        print("="*60)
    else:
        print("\n✗ No record found in agent_run_log")
        print("="*60)
        print("TEST 2A: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 2A FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
