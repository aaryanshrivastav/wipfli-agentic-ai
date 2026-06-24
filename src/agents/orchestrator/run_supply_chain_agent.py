from ..services.memory_services import *

from context_builder import (
    build_agent_context
)

from output_validator import (
    validate_agent_output
)

from supply_chain_agent import (
    supply_chain_agent
)

from tool_registry import (
    TOOL_REGISTRY
)

def run_supply_chain_agent(

    connection,

    product_key,

    store_key,

    supplier_key
):
        run_id = start_run(connection)
        inventory_risk = execute_tool(connection, run_id, "get_inventory_risk", TOOL_REGISTRY["get_inventory_risk"],
        product_key=product_key,store_key=store_key)
        supplier_risk = execute_tool(connection, run_id, "get_supplier_risk", TOOL_REGISTRY["get_supplier_risk"],supplier_key=supplier_key)
        forecast = execute_tool(

        connection,

        run_id,

        "get_forecast",

        TOOL_REGISTRY[
            "get_forecast"
        ],

        product_key=product_key,

        store_key=store_key
    )
        recommendation = execute_tool(

        connection,

        run_id,

        "get_recommendation",

        TOOL_REGISTRY[
            "get_recommendation"
        ],

        product_key=product_key,

        store_key=store_key
    )
        purchase_orders = execute_tool(

        connection,

        run_id,

        "get_open_purchase_orders",

        TOOL_REGISTRY[
            "get_open_purchase_orders"
        ],

        product_key=product_key
    )
        context = build_agent_context(

        inventory_risk,

        supplier_risk,

        forecast,

        recommendation,

        purchase_orders
    )
        result = supply_chain_agent(
        context
    )
        validate_agent_output(
        result
    )
        log_agent_action(

        connection,

        run_id,

        result["action"],

        result["confidence"],

        result["reasoning"],

        context
    )
        finish_run(
        connection,
        run_id
    )
        return result