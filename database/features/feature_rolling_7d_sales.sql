CREATE TABLE IF NOT EXISTS agentdb.features.feature_rolling_7d_sales
(
    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,
    calendar_key BIGINT NOT NULL,

    rolling_7d_sales DOUBLE,

    rolling_7d_avg DOUBLE,

    rolling_7d_stddev DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;