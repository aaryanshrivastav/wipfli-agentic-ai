CREATE TABLE IF NOT EXISTS agentdb.silver.sales
(
    sales_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_id BIGINT NOT NULL,
    store_id BIGINT NOT NULL,
    calendar_id BIGINT NOT NULL,

    sales_qty INT NOT NULL,

    created_at TIMESTAMP NOT NULL,

    load_batch_id STRING
)
USING DELTA;