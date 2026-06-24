CREATE TABLE IF NOT EXISTS agentdb.gold.dim_calendar
(
    calendar_key BIGINT GENERATED ALWAYS AS IDENTITY,

    calendar_id BIGINT NOT NULL,

    date DATE NOT NULL,

    wm_yr_wk INT,

    weekday STRING,

    wday INT,

    month INT,

    year INT,

    event_name_1 STRING,
    event_type_1 STRING,

    event_name_2 STRING,
    event_type_2 STRING,

    snap_ca INT,
    snap_tx INT,
    snap_wi INT
)
USING DELTA;