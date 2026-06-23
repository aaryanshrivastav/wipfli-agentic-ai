CREATE TABLE IF NOT EXISTS agentdb.features.feature_price_change
(
    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,
    calendar_key BIGINT NOT NULL,

    current_price DOUBLE,

    previous_price DOUBLE,

    price_change_pct DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;