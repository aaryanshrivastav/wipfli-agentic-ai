CREATE TABLE IF NOT EXISTS agentdb.bronze.calendar_raw
(
    date DATE,
    wm_yr_wk INT,
    weekday STRING,
    wday INT,
    month INT,
    year INT,

    d STRING,

    event_name_1 STRING,
    event_type_1 STRING,

    event_name_2 STRING,
    event_type_2 STRING,

    snap_CA INT,
    snap_TX INT,
    snap_WI INT,

    ingestion_timestamp TIMESTAMP,
    source_file STRING,
    source_system STRING,
    load_batch_id STRING
)
USING DELTA;