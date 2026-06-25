from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentAction:

    run_id: str

    action_type: str

    confidence_score: float

    reasoning: str

    action_payload: str

    created_at: datetime