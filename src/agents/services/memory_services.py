import uuid
import time

from memory.run_logger import (
    create_agent_run,
    complete_agent_run
)

from memory.tool_logger import (
    log_tool_execution
)

from memory.action_logger import (
    log_agent_action
)

def start_run(connection):

    run_id = str(uuid.uuid4())

    create_agent_run(
        connection,
        run_id
    )

    return run_id

def finish_run(
    connection,
    run_id,
    status="SUCCESS"
):
    complete_agent_run(
        connection,
        run_id,
        status
    )

def execute_tool(
    connection,

    run_id,

    tool_name,

    tool_function,

    **kwargs
):
    start = time.time()

    result = tool_function(
        connection,
        **kwargs
    )

    execution_time_ms = int(
        (
            time.time() - start
        ) * 1000
    )

    log_tool_execution(
        connection,

        run_id,

        tool_name,

        kwargs,

        result,

        execution_time_ms
    )

    return result