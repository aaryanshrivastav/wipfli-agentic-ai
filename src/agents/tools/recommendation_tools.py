"""Recommendation Tool

Retrieves recommendation data using Spark SQL.
"""

def get_recommendation(
    spark,
    product_key: int,
    store_key: int
):
    """Get latest recommendation for a product at a store.
    
    Args:
        spark: SparkSession object
        product_key: Product identifier
        store_key: Store identifier
        
    Returns:
        dict: Latest recommendation data
    """
    query = f"""
    SELECT *

    FROM agentdb.intelligence.recommendation_registry

    WHERE product_key = {product_key}
      AND store_key = {store_key}

    ORDER BY generated_at DESC

    LIMIT 1
    """

    result_df = spark.sql(query)
    row = result_df.first()

    return dict(row.asDict()) if row else {}
