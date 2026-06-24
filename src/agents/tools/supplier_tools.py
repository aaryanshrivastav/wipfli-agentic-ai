def get_supplier_risk(
    connection,
    supplier_key: int
):
    query = f"""
    SELECT *

    FROM agentdb.intelligence.supplier_risk

    WHERE supplier_key = {supplier_key}
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        row = cursor.fetchone()

    return dict(row)