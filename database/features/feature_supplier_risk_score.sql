CREATE TABLE IF NOT EXISTS agentdb.features.feature_supplier_risk_score
(
    supplier_key BIGINT NOT NULL,

    risk_score DOUBLE,

    disruption_count INT,

    avg_delay_days DOUBLE,

    supplier_risk_score DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;