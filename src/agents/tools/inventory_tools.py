"""Inventory Risk Tool

Retrieves inventory risk data using Spark SQL.
"""

def get_inventory_risk(
    spark,
    product_key: int,
    store_key: int
):
    """Get inventory risk for a product at a store.
    
    Args:
        spark: SparkSession object
        product_key: Product identifier
        store_key: Store identifier
        
    Returns:
        dict: Inventory risk data including qty, forecasts, risk level
    """
    query = f"""
    SELECT
        product_key,
        store_key,

        inventory_qty,

        forecast_7d,
        forecast_14d,
        forecast_30d,

        projected_days_to_stockout,

        risk_level

    FROM agentdb.intelligence.inventory_risk

    WHERE product_key = {product_key}
      AND store_key = {store_key}
    """

    result_df = spark.sql(query)
    row = result_df.first()

    return dict(row.asDict()) if row else {}
