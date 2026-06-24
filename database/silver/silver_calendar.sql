CREATE TABLE IF NOT EXISTS agentdb.silver.calendar
(
    calendar_id BIGINT GENERATED ALWAYS AS IDENTITY,

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
    snap_wi INT,

    created_at TIMESTAMP NOT NULL
)
USING DELTA;