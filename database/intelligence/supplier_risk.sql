CREATE TABLE IF NOT EXISTS agentdb.intelligence.supplier_risk
(
    supplier_risk_id BIGINT GENERATED ALWAYS AS IDENTITY,

    supplier_key BIGINT,

    lead_time_days INT,

    disruption_probability DOUBLE,

    delay_frequency DOUBLE,

    reliability_score DOUBLE,

    supplier_risk_score DOUBLE,

    risk_level STRING,

    created_at TIMESTAMP
)
USING DELTA;