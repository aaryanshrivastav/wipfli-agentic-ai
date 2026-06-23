CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_stockout_risk
(
    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,

    inventory_qty INT,

    forecast_demand_7d DOUBLE,

    days_of_cover DOUBLE,

    stockout_probability DOUBLE,

    risk_level STRING,

    created_at TIMESTAMP
)
USING DELTA;