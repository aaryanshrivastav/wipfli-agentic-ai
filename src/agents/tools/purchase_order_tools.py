def get_open_purchase_orders(
    connection,
    product_key: int
):
    query = f"""
    SELECT

        COUNT(*) AS open_po_count

    FROM agentdb.gold.fact_purchase_orders

    WHERE product_key = {product_key}
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        row = cursor.fetchone()

    return dict(row)