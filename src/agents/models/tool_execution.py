from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolExecution:

    run_id: str

    tool_name: str

    tool_input: str

    tool_output: str

    execution_time_ms: int

    executed_at: datetime