VALID_ACTIONS = {

    "REORDER",

    "EXPEDITE_PO",

    "SUPPLIER_ALERT",

    "NO_ACTION"
}

def validate_agent_output(
    result: dict
):
    required = {

        "action",

        "priority",

        "confidence",

        "reasoning"
    }

    if not required.issubset(
        result.keys()
    ):
        raise Exception(
            "Missing fields"
        )

    if (
        result["action"]
        not in VALID_ACTIONS
    ):
        raise Exception(
            "Invalid action"
        )

    return True