CREATE TABLE IF NOT EXISTS agentdb.silver.store_inventory_snapshot
(
    inventory_snapshot_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_id BIGINT NOT NULL,
    store_id BIGINT NOT NULL,

    snapshot_date DATE NOT NULL,

    inventory_qty INT NOT NULL,

    days_of_cover DOUBLE,

    created_at TIMESTAMP NOT NULL,

    load_batch_id STRING
)
USING DELTA;