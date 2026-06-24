from ..agents.orchestrator.run_supply_chain_agent import (
    run_supply_chain_agent
)

result = run_supply_chain_agent(

    connection,

    product_key=1,

    store_key=1,

    supplier_key=1
)

print(result)