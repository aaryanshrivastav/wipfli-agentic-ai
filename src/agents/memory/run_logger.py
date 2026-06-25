"""Agent Run Logger

Logs agent run lifecycle to agent_run_log table using Spark SQL.

Table Schema:
- run_id, agent_name, trigger_type, run_timestamp
- execution_duration_ms, run_status, error_message
- recommendations_generated, recommendations_accepted, recommendations_rejected
- created_at
"""

def create_agent_run(
    spark,
    run_id: str,
    agent_name: str = "supply_chain_agent",
    trigger_type: str = "manual"
):
    """Create a new agent run record.
    
    Args:
        spark: SparkSession object
        run_id: Unique run identifier
        agent_name: Name of the agent
        trigger_type: How the run was triggered
    """
    query = f"""
    INSERT INTO agentdb.silver.agent_run_log
    (
        run_id,
        agent_name,
        trigger_type,
        run_timestamp,
        execution_duration_ms,
        recommendations_generated,
        recommendations_accepted,
        recommendations_rejected,
        run_status,
        error_message,
        created_at
    )
    VALUES
    (
        '{run_id}',
        '{agent_name}',
        '{trigger_type}',
        CURRENT_TIMESTAMP(),
        NULL,
        0,
        0,
        0,
        'RUNNING',
        NULL,
        CURRENT_TIMESTAMP()
    )
    """

    spark.sql(query)


def complete_agent_run(
    spark,
    run_id: str,
    status: str = "SUCCESS",
    execution_duration_ms: float = None,
    error_message: str = None
):
    """Complete an agent run by updating its status.
    
    Args:
        spark: SparkSession object
        run_id: Run identifier
        status: Final status (SUCCESS, FAILED, etc.)
        execution_duration_ms: Total execution time
        error_message: Error message if failed
    """
    error_clause = f"'{error_message}'" if error_message else "NULL"
    duration_clause = str(execution_duration_ms) if execution_duration_ms else "NULL"
    
    query = f"""
    UPDATE agentdb.silver.agent_run_log

    SET
        run_status = '{status}',
        execution_duration_ms = {duration_clause},
        error_message = {error_clause}

    WHERE run_id = '{run_id}'
    """

    spark.sql(query)
