CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_action_effectiveness
(
    action_type STRING,

    recommendations_generated BIGINT,

    recommendations_completed BIGINT,

    recommendations_successful BIGINT,

    success_rate DOUBLE,

    avg_resolution_days DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;