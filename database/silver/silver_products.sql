CREATE TABLE IF NOT EXISTS agentdb.silver.product
(
    product_id BIGINT GENERATED ALWAYS AS IDENTITY,

    item_id STRING NOT NULL,

    dept_id STRING NOT NULL,

    cat_id STRING NOT NULL,

    supplier_id BIGINT,

    effective_start_date TIMESTAMP NOT NULL,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,

    change_type STRING,

    is_deleted BOOLEAN NOT NULL
)
USING DELTA;