from pathlib import Path

CATALOG = "agentdb"
SCHEMA = "bronze"
TABLE_NAME = "sales_raw"

OUTPUT_FILE = Path("database/bronze/sales_raw.sql")

NUM_DAYS = 1913


def generate_day_columns(num_days: int) -> str:
    columns = []

    for day in range(1, num_days + 1):
        columns.append(f"    d_{day} INT")

    return ",\n".join(columns)


def generate_ddl() -> str:
    day_columns = generate_day_columns(NUM_DAYS)

    ddl = f"""CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.{TABLE_NAME}
(
    id STRING,

    item_id STRING,
    dept_id STRING,
    cat_id STRING,

    store_id STRING,
    state_id STRING,

{day_columns},

    ingestion_timestamp TIMESTAMP,
    source_file STRING,
    source_system STRING,
    load_batch_id STRING
)
USING DELTA;
"""

    return ddl


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    ddl = generate_ddl()

    OUTPUT_FILE.write_text(ddl, encoding="utf-8")

    print(f"Generated: {OUTPUT_FILE}")
    print(f"Columns generated: {NUM_DAYS}")


if __name__ == "__main__":
    main()