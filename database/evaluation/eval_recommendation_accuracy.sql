CREATE TABLE IF NOT EXISTS agentdb.evaluation.eval_recommendation_accuracy
(
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY,

    action_id BIGINT,

    action_type STRING,

    entity_type STRING,
    entity_id BIGINT,

    recommendation_timestamp TIMESTAMP,

    actual_outcome STRING,

    success_flag BOOLEAN,

    evaluation_score DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;