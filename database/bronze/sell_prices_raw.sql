CREATE TABLE IF NOT EXISTS agentdb.bronze.sell_prices_raw
(
    store_id STRING,
    item_id STRING,
    wm_yr_wk INT,
    sell_price DOUBLE,

    ingestion_timestamp TIMESTAMP,
    source_file STRING,
    source_system STRING,
    load_batch_id STRING
)
USING DELTA;