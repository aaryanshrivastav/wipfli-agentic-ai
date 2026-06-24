CREATE TABLE IF NOT EXISTS agentdb.silver.agent_action_log
(
    action_id BIGINT GENERATED ALWAYS AS IDENTITY,

    entity_type STRING NOT NULL,
    entity_id BIGINT NOT NULL,

    action_type STRING NOT NULL,

    recommendation_reason STRING,

    recommendation_timestamp TIMESTAMP NOT NULL,

    action_status STRING NOT NULL,

    resolved_timestamp TIMESTAMP,

    created_at TIMESTAMP NOT NULL
)
USING DELTA;