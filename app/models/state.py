from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    GENERATING = "generating"
    TESTING = "testing"
    CORRECTING = "correcting"
    SUCCESS = "success"
    FAILED = "failed"


class AttemptRecord(BaseModel):
    iteration: int
    status: PipelineStatus
    code: str = ""
    test_code: str = ""
    test_logs: str = ""
    exit_code: int | None = None


class PipelineState(BaseModel):
    feature_request: str = ""
    current_code: str = ""
    current_test_code: str = ""
    iteration_count: int = 0
    test_logs: str = ""
    status: PipelineStatus = PipelineStatus.GENERATING
    history: List[AttemptRecord] = Field(default_factory=list)

    def add_attempt(self, attempt: AttemptRecord) -> None:
        self.history.append(attempt)
