CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_data_quality
(
    table_name STRING,

    validation_date DATE,

    total_records BIGINT,

    failed_records BIGINT,

    duplicate_records BIGINT,

    null_records BIGINT,

    quality_score DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;