CREATE TABLE IF NOT EXISTS agentdb.silver.price
(
    price_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_id BIGINT NOT NULL,
    store_id BIGINT NOT NULL,

    wm_yr_wk INT NOT NULL,

    sell_price DOUBLE NOT NULL,

    created_at TIMESTAMP NOT NULL,

    load_batch_id STRING
)
USING DELTA;