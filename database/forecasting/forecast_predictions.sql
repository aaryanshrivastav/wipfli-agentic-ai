CREATE TABLE IF NOT EXISTS agentdb.forecasting.forecast_predictions
(
    prediction_id BIGINT,

    product_key BIGINT,
    store_key BIGINT,

    forecast_date DATE,

    forecast_horizon_days INT,

    predicted_demand DOUBLE,

    model_name STRING,

    created_at TIMESTAMP
)
USING DELTA;