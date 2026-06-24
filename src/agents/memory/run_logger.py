from datetime import datetime


def create_agent_run(
    connection,
    run_id: str
):
    query = f"""
    INSERT INTO agentdb.silver.agent_run_log
    (
        run_id,
        started_at,
        status
    )
    VALUES
    (
        '{run_id}',
        CURRENT_TIMESTAMP(),
        'RUNNING'
    )
    """

    with connection.cursor() as cursor:
        cursor.execute(query)


def complete_agent_run(
    connection,
    run_id: str,
    status: str = "SUCCESS"
):
    query = f"""
    UPDATE agentdb.silver.agent_run_log

    SET
        completed_at = CURRENT_TIMESTAMP(),
        status = '{status}'

    WHERE run_id = '{run_id}'
    """

    with connection.cursor() as cursor:
        cursor.execute(query)