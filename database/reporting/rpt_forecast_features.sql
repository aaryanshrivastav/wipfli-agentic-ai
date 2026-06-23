CREATE TABLE IF NOT EXISTS agentdb.gold.fact_agent_metrics
(
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY,

    execution_date DATE,

    recommendations_generated BIGINT,

    recommendations_accepted BIGINT,

    recommendations_rejected BIGINT,

    tool_calls BIGINT,

    average_latency_ms DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;