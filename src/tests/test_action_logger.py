"""TEST 2C: Action Logger Test

Tests agent_action_log table functionality.

Table Schema:
- action_id (auto-increment)
- entity_type, entity_id
- action_type, recommendation_reason
- recommendation_timestamp, action_status
- resolved_timestamp, created_at

Expected Behavior:
1. Insert an agent action record
2. Verify data in agentdb.silver.agent_action_log
"""

import uuid

# TEST EXECUTION
print("="*60)
print("TEST 2C: ACTION LOGGER")
print("="*60)

try:
    # Prepare test data
    entity_type = "inventory"
    entity_id = 1
    action_type = "REORDER"
    recommendation_reason = "Inventory risk requires reorder"
    action_status = "PENDING"
    
    print(f"\nStep 1: Logging agent action...")
    print(f"  Entity: {entity_type} (ID: {entity_id})")
    print(f"  Action: {action_type}")
    print(f"  Reason: {recommendation_reason}")
    print(f"  Status: {action_status}")
    
    # Insert action log
    insert_query = f"""
    INSERT INTO agentdb.silver.agent_action_log
    (
        entity_type,
        entity_id,
        action_type,
        recommendation_reason,
        recommendation_timestamp,
        action_status,
        resolved_timestamp,
        created_at
    )
    VALUES
    (
        '{entity_type}',
        {entity_id},
        '{action_type}',
        '{recommendation_reason}',
        CURRENT_TIMESTAMP(),
        '{action_status}',
        NULL,
        CURRENT_TIMESTAMP()
    )
    """
    
    spark.sql(insert_query)
    print("\n✓ INSERT successful")
    
    # Step 2: Verify data in table
    print("\nStep 2: Verifying data in agent_action_log...")
    verify_query = f"""
    SELECT *
    FROM agentdb.silver.agent_action_log
    WHERE entity_type = '{entity_type}'
      AND entity_id = {entity_id}
      AND action_type = '{action_type}'
    ORDER BY created_at DESC
    LIMIT 1
    """
    
    result_df = spark.sql(verify_query)
    result = result_df.first()
    
    if result:
        print("\n✓ Record found in agent_action_log:")
        print("-" * 60)
        print(f"  action_id: {result['action_id']}")
        print(f"  entity_type: {result['entity_type']}")
        print(f"  entity_id: {result['entity_id']}")
        print(f"  action_type: {result['action_type']}")
        print(f"  recommendation_reason: {result['recommendation_reason']}")
        print(f"  action_status: {result['action_status']}")
        print(f"  recommendation_timestamp: {result['recommendation_timestamp']}")
        print(f"  created_at: {result['created_at']}")
        
        # Check fields
        checks = [
            ('entity_type', result['entity_type'] == entity_type),
            ('entity_id', result['entity_id'] == entity_id),
            ('action_type', result['action_type'] == action_type),
            ('recommendation_reason', result['recommendation_reason'] == recommendation_reason),
            ('action_status', result['action_status'] == action_status),
            ('recommendation_timestamp', result['recommendation_timestamp'] is not None),
            ('created_at', result['created_at'] is not None)
        ]
        
        print("\n" + "-" * 60)
        for field, passed in checks:
            print(f"  {'✓' if passed else '✗'} {field}")
        
        all_passed = all(check[1] for check in checks)
        
        print("\n" + "="*60)
        print("TEST 2C: PASS" if all_passed else "TEST 2C: FAIL")
        print("="*60)
    else:
        print("\n✗ No record found in agent_action_log")
        print("="*60)
        print("TEST 2C: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 2C FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
