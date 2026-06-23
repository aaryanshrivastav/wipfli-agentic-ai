CREATE TABLE IF NOT EXISTS agentdb.gold.fact_pipeline_metrics
(
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY,

    pipeline_name STRING,

    execution_date DATE,

    records_processed BIGINT,

    failed_records BIGINT,

    runtime_seconds DOUBLE,

    quality_score DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;