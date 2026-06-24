from ..agents.tools.inventory_tools import (
    get_inventory_risk
)

result = get_inventory_risk(
    connection,
    product_key=1,
    store_key=1
)

print(result)