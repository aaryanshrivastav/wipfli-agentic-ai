CREATE TABLE IF NOT EXISTS agentdb.gold.dim_supplier
(
    supplier_key BIGINT GENERATED ALWAYS AS IDENTITY,

    supplier_id BIGINT NOT NULL,

    supplier_code STRING NOT NULL,

    supplier_name STRING NOT NULL,

    supplier_category STRING,

    lead_time_days INT,

    risk_score DOUBLE,

    supplier_status STRING,

    effective_start_date TIMESTAMP,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN,
    is_deleted BOOLEAN,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA;