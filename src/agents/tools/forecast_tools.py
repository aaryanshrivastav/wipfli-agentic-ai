"""Forecast Tool

Retrieves demand forecast data using Spark SQL.
"""

def get_forecast(
    spark,
    product_key: int,
    store_key: int
):
    """Get demand forecast for a product at a store.
    
    Args:
        spark: SparkSession object
        product_key: Product identifier
        store_key: Store identifier
        
    Returns:
        dict: Forecast data for 7d, 14d, and 30d periods
    """
    query = f"""
    SELECT

        forecast_7d,
        forecast_14d,
        forecast_30d

    FROM agentdb.intelligence.inventory_risk

    WHERE product_key = {product_key}
      AND store_key = {store_key}
    """

    result_df = spark.sql(query)
    row = result_df.first()

    return dict(row.asDict()) if row else {}
