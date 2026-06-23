CREATE TABLE IF NOT EXISTS agentdb.silver.system_event_log
(
    event_id BIGINT GENERATED ALWAYS AS IDENTITY,

    event_type STRING NOT NULL,

    event_source STRING NOT NULL,

    event_description STRING,

    event_timestamp TIMESTAMP NOT NULL,

    severity STRING,

    created_at TIMESTAMP NOT NULL
)
USING DELTA;