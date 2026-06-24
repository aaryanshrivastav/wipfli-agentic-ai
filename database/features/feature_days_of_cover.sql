CREATE TABLE IF NOT EXISTS agentdb.features.feature_days_of_cover
(
    product_key BIGINT NOT NULL,

    store_key BIGINT,

    dc_key BIGINT,

    calendar_key BIGINT NOT NULL,

    inventory_qty INT,

    avg_daily_sales DOUBLE,

    days_of_cover DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;