from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    PLANNING = "planning"
    GENERATING = "generating"
    TESTING = "testing"
    CORRECTING = "correcting"
    BUILDING_UI = "building_ui"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"


class AgentName(str, Enum):
    PM = "pm"
    CODER = "coder"
    QA = "qa"
    FRONTEND = "frontend"


class AttemptRecord(BaseModel):
    iteration: int
    status: PipelineStatus
    agent: AgentName | None = None
    code: str = ""
    test_code: str = ""
    test_logs: str = ""
    exit_code: int | None = None


class PipelineState(BaseModel):
    run_id: str = ""
    feature_request: str = ""
    technical_blueprint: str = ""
    current_code: str = ""
    current_test_code: str = ""
    frontend_code: str = ""
    openapi_schema: Dict[str, Any] | None = None
    deployment_id: str | None = None
    live_api_path: str | None = None
    live_ui_path: str | None = None
    iteration_count: int = 0
    test_logs: str = ""
    status: PipelineStatus = PipelineStatus.PLANNING
    active_agent: AgentName | None = None
    history: List[AttemptRecord] = Field(default_factory=list)

    def add_attempt(self, attempt: AttemptRecord) -> None:
        self.history.append(attempt)
