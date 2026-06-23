CREATE TABLE IF NOT EXISTS agentdb.features.feature_inventory_turnover
(
    product_key BIGINT NOT NULL,

    store_key BIGINT,

    calendar_key BIGINT NOT NULL,

    inventory_turnover_ratio DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;