CREATE TABLE IF NOT EXISTS
agentdb.intelligence.recommendation_outcome
(
    outcome_id BIGINT GENERATED ALWAYS AS IDENTITY,

    recommendation_id BIGINT,

    outcome_status STRING,

    outcome_reason STRING,

    stockout_prevented BOOLEAN,

    inventory_reduced BOOLEAN,

    evaluated_at TIMESTAMP
)
USING DELTA;