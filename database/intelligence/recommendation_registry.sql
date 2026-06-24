CREATE TABLE IF NOT EXISTS agentdb.intelligence.recommendation_registry
(
    recommendation_id BIGINT GENERATED ALWAYS AS IDENTITY,

    recommendation_type STRING,

    product_key BIGINT,
    store_key BIGINT,

    supplier_key BIGINT,

    recommendation_text STRING,

    urgency_score DOUBLE,

    recommendation_status STRING,

    generated_at TIMESTAMP
)
USING DELTA;