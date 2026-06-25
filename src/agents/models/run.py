from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentRun:

    run_id: str

    started_at: datetime

    completed_at: datetime | None

    status: str