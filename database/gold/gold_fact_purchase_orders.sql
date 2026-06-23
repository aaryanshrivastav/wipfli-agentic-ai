CREATE TABLE IF NOT EXISTS agentdb.gold.fact_purchase_orders
(
    po_fact_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_key BIGINT NOT NULL,

    supplier_key BIGINT NOT NULL,

    dc_key BIGINT NOT NULL,

    ordered_qty INT NOT NULL,

    received_qty INT,

    lead_time_days INT,

    delay_days INT,

    order_date DATE,

    expected_delivery_date DATE,

    actual_delivery_date DATE,

    po_status STRING,

    created_at TIMESTAMP
)
USING DELTA;