from app.agents.base import BaseAgent
from app.agents.prompts import QA_SYSTEM_PROMPT, QA_USER_PROMPT
from app.sandbox.executor import SandboxExecutor, SandboxResult


class QAAgent(BaseAgent):
    """Generates pytest suites and executes them in an isolated sandbox."""

    name = "qa"

    def __init__(self) -> None:
        super().__init__()
        self._sandbox = SandboxExecutor()

    def generate_tests(self, blueprint: str, feature_request: str) -> str:
        return self._call_llm(
            system=QA_SYSTEM_PROMPT,
            user=QA_USER_PROMPT.format(
                feature_request=feature_request,
                blueprint=blueprint,
            ),
            output_format="python",
        )

    def run_tests(self, app_code: str, test_code: str) -> SandboxResult:
        return self._sandbox.run_tests(app_code, test_code)
