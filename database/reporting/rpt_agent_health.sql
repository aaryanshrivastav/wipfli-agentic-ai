CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_agent_health
(
    execution_date DATE,

    recommendations_generated BIGINT,

    tool_calls BIGINT,

    average_latency_ms DOUBLE,

    recommendation_success_rate DOUBLE,

    health_status STRING,

    created_at TIMESTAMP
)
USING DELTA;