CREATE TABLE IF NOT EXISTS agentdb.features.feature_stockout_probability
(
    product_key BIGINT NOT NULL,

    store_key BIGINT NOT NULL,

    calendar_key BIGINT NOT NULL,

    inventory_qty INT,

    forecast_demand DOUBLE,

    stockout_probability DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;