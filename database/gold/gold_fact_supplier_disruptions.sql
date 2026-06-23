CREATE TABLE IF NOT EXISTS agentdb.gold.fact_supplier_disruptions
(
    disruption_fact_id BIGINT GENERATED ALWAYS AS IDENTITY,

    supplier_key BIGINT NOT NULL,

    disruption_type STRING,

    severity_score DOUBLE,

    delay_days INT,

    disruption_start_date DATE,

    disruption_end_date DATE,

    disruption_status STRING,

    created_at TIMESTAMP
)
USING DELTA;