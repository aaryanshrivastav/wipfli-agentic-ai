CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_replenishment_candidates
(
    product_key BIGINT NOT NULL,

    store_key BIGINT,

    dc_key BIGINT,

    inventory_qty INT,

    reorder_point DOUBLE,

    recommended_order_qty DOUBLE,

    urgency_score DOUBLE,

    recommendation_type STRING,

    created_at TIMESTAMP
)
USING DELTA;