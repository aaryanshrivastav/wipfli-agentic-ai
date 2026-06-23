CREATE TABLE IF NOT EXISTS agentdb.silver.dc_inventory_snapshot
(
    dc_inventory_snapshot_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_id BIGINT NOT NULL,
    dc_id BIGINT NOT NULL,

    snapshot_date DATE NOT NULL,

    inventory_qty INT NOT NULL,

    created_at TIMESTAMP NOT NULL,

    load_batch_id STRING
)
USING DELTA;