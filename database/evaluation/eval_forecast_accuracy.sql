CREATE TABLE IF NOT EXISTS agentdb.evaluation.eval_forecast_accuracy
(
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY,

    evaluation_date DATE NOT NULL,

    product_key BIGINT,
    store_key BIGINT,

    forecast_horizon_days INT,

    actual_value DOUBLE,
    predicted_value DOUBLE,

    mae DOUBLE,
    rmse DOUBLE,
    mape DOUBLE,
    wmape DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;