"""Agent Tool Execution Logger

Logs tool executions to agent_tool_execution_log table using Spark SQL.

Table Schema:
- tool_execution_id (auto-increment)
- run_id, tool_name
- entity_type, entity_id
- execution_start_timestamp, execution_end_timestamp
- execution_duration_ms, success_flag, error_message
- created_at
"""

import json
from datetime import datetime

def log_tool_execution(
    spark,
    run_id: str,
    tool_name: str,
    entity_type: str,
    entity_id: int,
    execution_duration_ms: float,
    success_flag: bool = True,
    error_message: str = None
):
    """Log a tool execution.
    
    Args:
        spark: SparkSession object
        run_id: Agent run identifier
        tool_name: Name of the tool executed
        entity_type: Type of entity (e.g., 'inventory', 'supplier')
        entity_id: Entity identifier
        execution_duration_ms: Execution time in milliseconds
        success_flag: Whether execution succeeded
        error_message: Error message if failed
    """
    error_clause = f"'{error_message}'" if error_message else "NULL"
    entity_type_clause = f"'{entity_type}'" if entity_type else "NULL"
    entity_id_clause = str(entity_id) if entity_id is not None else "NULL"
    
    query = f"""
    INSERT INTO agentdb.silver.agent_tool_execution_log
    (
        run_id,
        tool_name,
        entity_type,
        entity_id,
        execution_start_timestamp,
        execution_end_timestamp,
        execution_duration_ms,
        success_flag,
        error_message,
        created_at
    )
    VALUES
    (
        '{run_id}',
        '{tool_name}',
        {entity_type_clause},
        {entity_id_clause},
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        {execution_duration_ms},
        {str(success_flag).lower()},
        {error_clause},
        CURRENT_TIMESTAMP()
    )
    """

    spark.sql(query)
