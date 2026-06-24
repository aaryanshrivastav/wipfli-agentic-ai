CREATE TABLE IF NOT EXISTS agentdb.forecasting.forecast_model_registry
(
    model_name STRING,

    is_active BOOLEAN,

    mae DOUBLE,
    rmse DOUBLE,
    mape DOUBLE,
    wmape DOUBLE,

    selected_at TIMESTAMP
)
USING DELTA;