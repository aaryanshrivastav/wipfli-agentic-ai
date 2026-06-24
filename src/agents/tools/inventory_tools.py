from databricks import sql


def get_inventory_risk(
    connection,
    product_key: int,
    store_key: int
):
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

    with connection.cursor() as cursor:
        cursor.execute(query)

        row = cursor.fetchone()

    return dict(row)