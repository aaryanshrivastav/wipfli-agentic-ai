import json
import time

def log_tool_execution(
    connection,
    run_id: str,

    tool_name: str,

    tool_input: dict,

    tool_output: dict,

    execution_time_ms: int
):
    query = f"""
    INSERT INTO agentdb.silver.agent_tool_execution_log
    (
        run_id,

        tool_name,

        tool_input,

        tool_output,

        execution_time_ms,

        executed_at
    )
    VALUES
    (
        '{run_id}',

        '{tool_name}',

        '{json.dumps(tool_input)}',

        '{json.dumps(tool_output)}',

        {execution_time_ms},

        CURRENT_TIMESTAMP()
    )
    """

    with connection.cursor() as cursor:
        cursor.execute(query)