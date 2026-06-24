CREATE TABLE IF NOT EXISTS agentdb.features.feature_daily_sales_velocity
(
    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,
    calendar_key BIGINT NOT NULL,

    sales_qty INT,

    previous_day_sales_qty INT,

    sales_velocity DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;