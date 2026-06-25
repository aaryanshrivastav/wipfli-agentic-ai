"""Purchase Order Tool

Retrieves open purchase order count using Spark SQL.
"""

def get_open_purchase_orders(
    spark,
    product_key: int
):
    """Get count of open purchase orders for a product.
    
    Args:
        spark: SparkSession object
        product_key: Product identifier
        
    Returns:
        dict: Open PO count
    """
    query = f"""
    SELECT

        COUNT(*) AS open_po_count

    FROM agentdb.gold.fact_purchase_orders

    WHERE product_key = {product_key}
    """

    result_df = spark.sql(query)
    row = result_df.first()

    return dict(row.asDict()) if row else {}
