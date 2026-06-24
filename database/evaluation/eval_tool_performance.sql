CREATE TABLE IF NOT EXISTS agentdb.evaluation.eval_tool_performance
(
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY,

    evaluation_date DATE NOT NULL,

    tool_name STRING NOT NULL,

    invocation_count BIGINT,

    average_latency_ms DOUBLE,

    success_count BIGINT,

    failure_count BIGINT,

    success_rate DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;