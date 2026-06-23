CREATE TABLE IF NOT EXISTS agentdb.gold.fact_sales
(
    sales_fact_id BIGINT GENERATED ALWAYS AS IDENTITY,

    product_key BIGINT NOT NULL,
    store_key BIGINT NOT NULL,
    calendar_key BIGINT NOT NULL,

    sales_qty INT NOT NULL,

    sales_revenue DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;