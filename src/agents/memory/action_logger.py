"""Agent Action Logger

Logs agent actions to agent_action_log table using Spark SQL.

Table Schema:
- action_id (auto-increment)
- entity_type, entity_id
- action_type, recommendation_reason
- recommendation_timestamp, action_status
- resolved_timestamp, created_at
"""

import json

def log_agent_action(
    spark,
    entity_type: str,
    entity_id: int,
    action_type: str,
    recommendation_reason: str,
    action_status: str = "PENDING"
):
    """Log an agent action/recommendation.
    
    Args:
        spark: SparkSession object
        entity_type: Type of entity (e.g., 'inventory', 'supplier')
        entity_id: Entity identifier
        action_type: Action recommended (REORDER, EXPEDITE_PO, etc.)
        recommendation_reason: Reasoning for the action
        action_status: Status of the action (PENDING, APPROVED, REJECTED)
    """
    query = f"""
    INSERT INTO agentdb.silver.agent_action_log
    (
        entity_type,
        entity_id,
        action_type,
        recommendation_reason,
        recommendation_timestamp,
        action_status,
        resolved_timestamp,
        created_at
    )
    VALUES
    (
        '{entity_type}',
        {entity_id},
        '{action_type}',
        '{recommendation_reason}',
        CURRENT_TIMESTAMP(),
        '{action_status}',
        NULL,
        CURRENT_TIMESTAMP()
    )
    """

    spark.sql(query)
