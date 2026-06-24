CREATE TABLE IF NOT EXISTS agentdb.evaluation.eval_agent_performance
(
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY,

    evaluation_date DATE NOT NULL,

    recommendations_generated BIGINT,

    recommendations_accepted BIGINT,

    recommendations_rejected BIGINT,

    average_latency_ms DOUBLE,

    average_tool_calls DOUBLE,

    decision_quality_score DOUBLE,

    success_rate DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;