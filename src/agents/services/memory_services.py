"""Memory Services

High-level functions for agent execution tracking.
All functions require spark parameter since they use Spark SQL.
"""

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

def start_run(spark, agent_name: str = "supply_chain_agent", trigger_type: str = "manual"):
    """Start a new agent run.
    
    Args:
        spark: SparkSession object
        agent_name: Name of the agent
        trigger_type: How the run was triggered
        
    Returns:
        str: Run ID (UUID)
    """
    run_id = str(uuid.uuid4())

    create_agent_run(
        spark=spark,
        run_id=run_id,
        agent_name=agent_name,
        trigger_type=trigger_type
    )

    return run_id

def finish_run(
    spark,
    run_id: str,
    status: str = "SUCCESS",
    execution_duration_ms: float = None,
    error_message: str = None
):
    """Complete an agent run.
    
    Args:
        spark: SparkSession object
        run_id: Run identifier
        status: Final status
        execution_duration_ms: Total execution time
        error_message: Error message if failed
    """
    complete_agent_run(
        spark=spark,
        run_id=run_id,
        status=status,
        execution_duration_ms=execution_duration_ms,
        error_message=error_message
    )

def execute_tool(
    spark,
    run_id: str,
    tool_name: str,
    tool_function,
    entity_type: str = None,
    entity_id: int = None,
    **kwargs
):
    """Execute a tool and log the execution.
    
    Args:
        spark: SparkSession object
        run_id: Run identifier
        tool_name: Name of the tool
        tool_function: The tool function to call
        entity_type: Entity type for logging
        entity_id: Entity ID for logging
        **kwargs: Arguments to pass to the tool
        
    Returns:
        Tool execution result
    """
    start = time.time()
    
    try:
        result = tool_function(spark, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
        raise

    execution_time_ms = (time.time() - start) * 1000

    log_tool_execution(
        spark=spark,
        run_id=run_id,
        tool_name=tool_name,
        entity_type=entity_type,
        entity_id=entity_id,
        execution_duration_ms=execution_time_ms,
        success_flag=success,
        error_message=error
    )

    return result
