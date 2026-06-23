CREATE TABLE IF NOT EXISTS agentdb.features.feature_demand_variability
(
    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,
    calendar_key BIGINT NOT NULL,

    avg_daily_sales DOUBLE,

    demand_stddev DOUBLE,

    coefficient_of_variation DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;