CREATE TABLE IF NOT EXISTS agentdb.silver.agent_tool_execution_log
(
    tool_execution_id BIGINT GENERATED ALWAYS AS IDENTITY,

    run_id STRING NOT NULL,

    tool_name STRING NOT NULL,

    entity_type STRING,
    entity_id BIGINT,

    execution_start_timestamp TIMESTAMP NOT NULL,
    execution_end_timestamp TIMESTAMP NOT NULL,

    execution_duration_ms DOUBLE,

    success_flag BOOLEAN NOT NULL,

    error_message STRING,

    created_at TIMESTAMP NOT NULL
)
USING DELTA;