"""Supplier Risk Tool

Retrieves supplier risk data using Spark SQL.
"""

def get_supplier_risk(
    spark,
    supplier_key: int
):
    """Get supplier risk for a supplier.
    
    Args:
        spark: SparkSession object
        supplier_key: Supplier identifier
        
    Returns:
        dict: Supplier risk data including risk level and metrics
    """
    query = f"""
    SELECT *

    FROM agentdb.intelligence.supplier_risk

    WHERE supplier_key = {supplier_key}
    """

    result_df = spark.sql(query)
    row = result_df.first()

    return dict(row.asDict()) if row else {}
