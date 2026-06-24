CREATE TABLE IF NOT EXISTS agentdb.gold.dim_distribution_center
(
    dc_key BIGINT GENERATED ALWAYS AS IDENTITY,

    dc_id BIGINT NOT NULL,

    dc_code STRING NOT NULL,

    dc_name STRING NOT NULL,

    state_id STRING NOT NULL,

    capacity_units BIGINT,

    effective_start_date TIMESTAMP,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN,
    is_deleted BOOLEAN,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA;