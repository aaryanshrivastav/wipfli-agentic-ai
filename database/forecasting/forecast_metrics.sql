CREATE TABLE IF NOT EXISTS agentdb.forecasting.forecast_metrics
(
    metric_id BIGINT,

    model_name STRING,

    evaluation_date DATE,

    mae DOUBLE,
    rmse DOUBLE,
    mape DOUBLE,
    wmape DOUBLE,

    created_at TIMESTAMP
)
USING DELTA;