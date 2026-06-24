CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_daily_supply_chain_status
(
    snapshot_date DATE NOT NULL,

    total_sales DOUBLE,

    total_inventory BIGINT,

    total_open_purchase_orders BIGINT,

    total_disruptions BIGINT,

    stores_at_risk BIGINT,

    products_at_risk BIGINT,

    suppliers_at_risk BIGINT,

    created_at TIMESTAMP
)
USING DELTA;