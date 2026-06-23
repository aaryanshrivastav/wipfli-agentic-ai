CREATE TABLE IF NOT EXISTS agentdb.gold.snapshot_supplier_risk
(
    snapshot_date DATE NOT NULL,

    supplier_key BIGINT,

    risk_score DOUBLE,

    disruption_probability DOUBLE,

    lead_time_risk DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;