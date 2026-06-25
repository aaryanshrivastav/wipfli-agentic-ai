from tools.inventory_tools import (
    get_inventory_risk
)

from tools.supplier_tools import (
    get_supplier_risk
)

from tools.forecast_tools import (
    get_forecast
)

from tools.recommendation_tools import (
    get_recommendation
)

from tools.purchase_order_tools import (
    get_open_purchase_orders
)


TOOL_REGISTRY = {

    "get_inventory_risk":
        get_inventory_risk,

    "get_supplier_risk":
        get_supplier_risk,

    "get_forecast":
        get_forecast,

    "get_recommendation":
        get_recommendation,

    "get_open_purchase_orders":
        get_open_purchase_orders
}