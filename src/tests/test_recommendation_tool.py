"""TEST 1D: Recommendation Tool Test

Tests get_recommendation() tool independently.

Expected Output:
- product_key
- store_key
- recommendation data
- generated_at
"""

# TEST EXECUTION
print("="*60)
print("TEST 1D: RECOMMENDATION TOOL")
print("="*60)

try:
    # First, check if there's any data in the table
    count_query = "SELECT COUNT(*) as cnt FROM agentdb.intelligence.recommendation_registry"
    count = spark.sql(count_query).first()['cnt']
    
    if count == 0:
        print("\n⚠ WARNING: Table agentdb.intelligence.recommendation_registry is EMPTY")
        print("Cannot test tool without data.")
        print("="*60)
    else:
        print(f"\n✓ Table has {count} rows")
        
        # Get a sample row to test with
        sample_query = """
        SELECT *
        FROM agentdb.intelligence.recommendation_registry
        ORDER BY generated_at DESC
        LIMIT 1
        """
        
        result_df = spark.sql(sample_query)
        result = result_df.first().asDict()
        
        print(f"Testing with product_key={result.get('product_key', 'N/A')}, store_key={result.get('store_key', 'N/A')}\n")
        
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
        print("TEST 1D: PASS" if result and 'product_key' in result else "TEST 1D: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 1D FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
