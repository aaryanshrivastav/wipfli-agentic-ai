CREATE TABLE IF NOT EXISTS agentdb.features.feature_rolling_30d_sales
(
    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,
    calendar_key BIGINT NOT NULL,

    rolling_30d_sales DOUBLE,

    rolling_30d_avg DOUBLE,

    rolling_30d_stddev DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;