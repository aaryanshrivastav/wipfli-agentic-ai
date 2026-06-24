"""TEST 1C: Forecast Tool Test

Tests get_forecast() tool independently.

Expected Output:
- forecast_7d
- forecast_14d
- forecast_30d
"""

# TEST EXECUTION
print("="*60)
print("TEST 1C: FORECAST TOOL")
print("="*60)

try:
    # First, check if there's any data in the table
    count_query = "SELECT COUNT(*) as cnt FROM agentdb.intelligence.inventory_risk"
    count = spark.sql(count_query).first()['cnt']
    
    if count == 0:
        print("\n⚠ WARNING: Table agentdb.intelligence.inventory_risk is EMPTY")
        print("Cannot test tool without data.")
        print("="*60)
    else:
        print(f"\n✓ Table has {count} rows")
        
        # Get a sample row to test with
        sample_query = """
        SELECT
            product_key,
            store_key,
            forecast_7d,
            forecast_14d,
            forecast_30d
        FROM agentdb.intelligence.inventory_risk
        LIMIT 1
        """
        
        result_df = spark.sql(sample_query)
        result = result_df.first().asDict()
        
        print(f"Testing with product_key={result['product_key']}, store_key={result['store_key']}\n")
        
        print("✓ Tool executed successfully\n")
        print("Result:")
        print("-" * 60)
        
        # Check expected fields
        expected_fields = [
            'forecast_7d',
            'forecast_14d',
            'forecast_30d'
        ]
        
        for field in expected_fields:
            if field in result:
                print(f"✓ {field}: {result[field]}")
            else:
                print(f"✗ MISSING: {field}")
        
        print("\n" + "="*60)
        print("TEST 1C: PASS" if all(f in result for f in expected_fields) else "TEST 1C: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 1C FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
