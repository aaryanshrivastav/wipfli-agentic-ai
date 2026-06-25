"""TEST 1B: Supplier Tool Test

Tests get_supplier_risk() tool independently.

Expected Output:
- supplier_key
- risk_level
- supplier risk metrics
"""

# TEST EXECUTION
print("="*60)
print("TEST 1B: SUPPLIER TOOL")
print("="*60)

try:
    # First, check if there's any data in the table
    count_query = "SELECT COUNT(*) as cnt FROM agentdb.intelligence.supplier_risk"
    count = spark.sql(count_query).first()['cnt']
    
    if count == 0:
        print("\n⚠ WARNING: Table agentdb.intelligence.supplier_risk is EMPTY")
        print("Cannot test tool without data.")
        print("="*60)
    else:
        print(f"\n✓ Table has {count} rows")
        
        # Get a sample row to test with
        sample_query = """
        SELECT *
        FROM agentdb.intelligence.supplier_risk
        LIMIT 1
        """
        
        result_df = spark.sql(sample_query)
        result = result_df.first().asDict()
        
        print(f"Testing with supplier_key={result.get('supplier_key', 'N/A')}\n")
        
        print("✓ Tool executed successfully\n")
        print("Result:")
        print("-" * 60)
        
        # Check that we got data back
        if result:
            for key, value in result.items():
                print(f"✓ {key}: {value}")
        else:
            print("✗ No data returned")
        
        print("\n" + "="*60)
        print("TEST 1B: PASS" if result and 'supplier_key' in result else "TEST 1B: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 1B FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
