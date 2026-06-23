CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_pipeline_health
(
    pipeline_name STRING,

    execution_date DATE,

    runtime_seconds DOUBLE,

    records_processed BIGINT,

    failed_records BIGINT,

    quality_score DOUBLE,

    health_status STRING,

    created_at TIMESTAMP
)
USING DELTA;