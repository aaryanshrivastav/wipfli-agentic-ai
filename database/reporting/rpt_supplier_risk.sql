CREATE TABLE IF NOT EXISTS agentdb.reporting.rpt_supplier_risk
(
    supplier_key BIGINT NOT NULL,

    risk_score DOUBLE,

    disruption_count INT,

    avg_delay_days DOUBLE,

    open_purchase_orders INT,

    impacted_products INT,

    supplier_risk_level STRING,

    created_at TIMESTAMP
)
USING DELTA;