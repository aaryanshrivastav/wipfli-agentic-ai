CREATE TABLE IF NOT EXISTS agentdb.silver.agent_run_log
(
    run_id STRING NOT NULL,

    agent_name STRING NOT NULL,

    trigger_type STRING NOT NULL,

    run_timestamp TIMESTAMP NOT NULL,

    execution_duration_ms DOUBLE,

    recommendations_generated INT,

    recommendations_accepted INT,

    recommendations_rejected INT,

    run_status STRING NOT NULL,

    error_message STRING,

    created_at TIMESTAMP NOT NULL
)
USING DELTA;