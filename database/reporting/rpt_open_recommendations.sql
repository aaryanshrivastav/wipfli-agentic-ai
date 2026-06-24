CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_open_recommendations
(
    action_id BIGINT NOT NULL,

    action_type STRING,

    entity_type STRING,

    entity_id BIGINT,

    recommendation_reason STRING,

    recommendation_timestamp TIMESTAMP,

    action_status STRING,

    age_days INT,

    created_at TIMESTAMP
)
USING DELTA;