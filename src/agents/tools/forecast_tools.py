def get_forecast(
    connection,
    product_key: int,
    store_key: int
):
    query = f"""
    SELECT

        forecast_7d,
        forecast_14d,
        forecast_30d

    FROM agentdb.intelligence.inventory_risk

    WHERE product_key = {product_key}
      AND store_key = {store_key}
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        row = cursor.fetchone()

    return dict(row)