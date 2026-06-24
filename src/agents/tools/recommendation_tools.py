def get_recommendation(
    connection,
    product_key: int,
    store_key: int
):
    query = f"""
    SELECT *

    FROM agentdb.intelligence.recommendation_registry

    WHERE product_key = {product_key}
      AND store_key = {store_key}

    ORDER BY generated_at DESC

    LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        row = cursor.fetchone()

    return dict(row)