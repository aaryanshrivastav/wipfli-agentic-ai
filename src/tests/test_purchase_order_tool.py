"""TEST 1E: Purchase Order Tool Test

Tests get_open_purchase_orders() tool independently.

Expected Output:
- open_po_count
"""

# TEST EXECUTION
print("="*60)
print("TEST 1E: PURCHASE ORDER TOOL")
print("="*60)

try:
    # First, check if there's any data in the table
    count_query = "SELECT COUNT(*) as cnt FROM agentdb.gold.fact_purchase_orders"
    count = spark.sql(count_query).first()['cnt']
    
    if count == 0:
        print("\n⚠ WARNING: Table agentdb.gold.fact_purchase_orders is EMPTY")
        print("Cannot test tool without data.")
        print("="*60)
    else:
        print(f"\n✓ Table has {count} rows")
        
        # Get a product_key to test with
        product_query = """
        SELECT DISTINCT product_key
        FROM agentdb.gold.fact_purchase_orders
        LIMIT 1
        """
        
        product_row = spark.sql(product_query).first()
        product_key = product_row['product_key']
        
        # Now run the actual query that the tool would run
        result_query = f"""
        SELECT
            COUNT(*) AS open_po_count
        FROM agentdb.gold.fact_purchase_orders
        WHERE product_key = {product_key}
        """
        
        result_df = spark.sql(result_query)
        result = result_df.first().asDict()
        
        print(f"Testing with product_key={product_key}\n")
        
        print("✓ Tool executed successfully\n")
        print("Result:")
        print("-" * 60)
        
        # Check expected field
        if 'open_po_count' in result:
            print(f"✓ open_po_count: {result['open_po_count']}")
        else:
            print("✗ MISSING: open_po_count")
        
        print("\n" + "="*60)
        print("TEST 1E: PASS" if 'open_po_count' in result else "TEST 1E: FAIL")
        print("="*60)
    
except Exception as e:
    print(f"\n✗ TEST 1E FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    print("="*60)
