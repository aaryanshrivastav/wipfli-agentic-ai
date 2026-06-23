CREATE TABLE IF NOT EXISTS agentdb.gold.fact_inventory_snapshot
(
    inventory_fact_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_key BIGINT NOT NULL,

    store_key BIGINT,
    dc_key BIGINT,

    calendar_key BIGINT NOT NULL,

    inventory_qty INT NOT NULL,

    days_of_cover DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;