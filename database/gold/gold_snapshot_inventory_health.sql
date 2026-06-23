CREATE TABLE IF NOT EXISTS agentdb.gold.snapshot_inventory_health
(
    snapshot_date DATE NOT NULL,

    product_key BIGINT,

    store_key BIGINT,

    inventory_qty INT,

    days_of_cover DOUBLE,

    inventory_health_score DOUBLE,

    risk_level STRING,

    created_at TIMESTAMP
)
USING DELTA;