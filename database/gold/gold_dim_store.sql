CREATE TABLE IF NOT EXISTS agentdb.gold.dim_store
(
    store_key BIGINT GENERATED ALWAYS AS IDENTITY,

    store_id BIGINT NOT NULL,

    store_code STRING NOT NULL,

    state_id STRING NOT NULL,

    dc_id BIGINT,

    effective_start_date TIMESTAMP,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN,
    is_deleted BOOLEAN,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA;