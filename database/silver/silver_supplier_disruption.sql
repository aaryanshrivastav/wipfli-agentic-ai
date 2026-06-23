CREATE TABLE IF NOT EXISTS agentdb.silver.supplier_disruption
(
    disruption_id BIGINT GENERATED ALWAYS AS IDENTITY,

    supplier_id BIGINT NOT NULL,

    disruption_type STRING NOT NULL,

    disruption_start_date DATE NOT NULL,
    disruption_end_date DATE,

    severity_score DOUBLE NOT NULL,

    delay_days INT NOT NULL,

    disruption_status STRING NOT NULL,

    created_at TIMESTAMP NOT NULL,

    load_batch_id STRING
)
USING DELTA;