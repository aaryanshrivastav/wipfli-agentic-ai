CREATE TABLE IF NOT EXISTS agentdb.silver.supplier
(
    supplier_id BIGINT GENERATED ALWAYS AS IDENTITY,

    supplier_code STRING NOT NULL,

    supplier_name STRING NOT NULL,

    supplier_category STRING,

    lead_time_days INT NOT NULL,

    risk_score DOUBLE NOT NULL,

    supplier_status STRING NOT NULL,

    effective_start_date TIMESTAMP NOT NULL,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,

    change_type STRING,

    is_deleted BOOLEAN NOT NULL
)
USING DELTA;