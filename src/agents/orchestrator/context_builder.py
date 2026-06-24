def build_agent_context(

    inventory_risk,

    supplier_risk,

    forecast,

    recommendation,

    purchase_orders
):
    return {

        "inventory_risk":
            inventory_risk,

        "supplier_risk":
            supplier_risk,

        "forecast":
            forecast,

        "recommendation":
            recommendation,

        "purchase_orders":
            purchase_orders
    }