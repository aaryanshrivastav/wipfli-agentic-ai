CREATE TABLE IF NOT EXISTS agentdb.gold.dim_product
(
    product_key BIGINT GENERATED ALWAYS AS IDENTITY,

    product_id BIGINT NOT NULL,

    item_id STRING NOT NULL,

    dept_id STRING NOT NULL,

    cat_id STRING NOT NULL,

    supplier_id BIGINT,

    effective_start_date TIMESTAMP,
    effective_end_date TIMESTAMP,

    is_current BOOLEAN,
    is_deleted BOOLEAN,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA;