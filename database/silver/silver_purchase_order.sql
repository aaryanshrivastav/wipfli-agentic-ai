CREATE TABLE IF NOT EXISTS agentdb.silver.purchase_order
(
    purchase_order_id BIGINT GENERATED ALWAYS AS IDENTITY,

    po_number STRING NOT NULL,

    supplier_id BIGINT NOT NULL,
    dc_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,

    ordered_qty INT NOT NULL,
    received_qty INT,

    lead_time_days INT NOT NULL,

    order_date DATE NOT NULL,
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE,

    po_status STRING NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,

    load_batch_id STRING
)
USING DELTA;