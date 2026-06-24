CREATE TABLE IF NOT EXISTS agentdb.intelligence.inventory_risk
(
    inventory_risk_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_key BIGINT,
    store_key BIGINT,

    inventory_qty DOUBLE,

    forecast_daily_demand DOUBLE,

    forecast_7d DOUBLE,
    forecast_14d DOUBLE,
    forecast_30d DOUBLE,

    days_of_cover DOUBLE,

    projected_days_to_stockout DOUBLE,

    safety_stock DOUBLE,

    risk_level STRING,

    created_at TIMESTAMP
)
USING DELTA;