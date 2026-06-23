CREATE TABLE IF NOT EXISTS agentdb.gold.fact_agent_actions
(
    agent_action_fact_id BIGINT GENERATED ALWAYS AS IDENTITY,

    action_id BIGINT NOT NULL,

    action_type STRING NOT NULL,

    entity_type STRING,

    entity_id BIGINT,

    action_status STRING,

    recommendation_timestamp TIMESTAMP,

    resolved_timestamp TIMESTAMP,

    created_at TIMESTAMP
)
USING DELTA;