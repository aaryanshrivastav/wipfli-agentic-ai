CREATE TABLE IF NOT EXISTS agentdb.silver.distribution_center
(
    dc_id BIGINT GENERATED ALWAYS AS IDENTITY,

    dc_code STRING NOT NULL,

    dc_name STRING NOT NULL,

    state_id STRING NOT NULL,

    capacity_units BIGINT NOT NULL,

    effective_start_date TIMESTAMP NOT NULL,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,

    change_type STRING,

    is_deleted BOOLEAN NOT NULL
)
USING DELTA;