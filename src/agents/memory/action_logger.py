import json

def log_agent_action(
    connection,

    run_id: str,

    action_type: str,

    confidence_score: float,

    reasoning: str,

    action_payload: dict
):
    query = f"""
    INSERT INTO agentdb.silver.agent_action_log
    (
        run_id,

        action_type,

        confidence_score,

        reasoning,

        action_payload,

        created_at
    )
    VALUES
    (
        '{run_id}',

        '{action_type}',

        {confidence_score},

        '{reasoning}',

        '{json.dumps(action_payload)}',

        CURRENT_TIMESTAMP()
    )
    """

    with connection.cursor() as cursor:
        cursor.execute(query)