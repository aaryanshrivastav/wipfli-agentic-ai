CREATE TABLE IF NOT EXISTS agentdb.features.feature_supplier_delay_frequency
(
    supplier_key BIGINT NOT NULL,

    delayed_pos INT,

    total_pos INT,

    delay_frequency DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;