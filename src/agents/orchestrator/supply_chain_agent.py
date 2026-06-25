def supply_chain_agent(
    context: dict
):
    inventory = context["inventory_risk"]
    supplier = context["supplier_risk"]
    if (inventory["projected_days_to_stockout"] < 7):
        return {
            "action":"EXPEDITE_PO",
            "priority":"CRITICAL",
            "confidence": 0.95,
            "reasoning":(
                    "Projected stockout "
                    "within 7 days."
                )
        }
    if (supplier["risk_level"] in ["HIGH", "CRITICAL"]):
        return {
            "action":"SUPPLIER_ALERT",
            "priority":"HIGH",
            "confidence":0.90,
            "reasoning":
                (
                    "Supplier risk "
                    "above threshold."
                )
        }
    if (inventory["risk_level"] in ["HIGH","CRITICAL"]):
        return {
            "action":"REORDER",
            "priority":"HIGH",
            "confidence": 0.88,
            "reasoning":
                (
                    "Inventory risk "
                    "requires reorder."
                )
        }
    return {
        "action":"NO_ACTION",
        "priority":"LOW",
        "confidence":0.99,
        "reasoning":
            (
                "Inventory healthy."
            )
    }