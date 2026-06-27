import logging

from app.agents.base import BaseAgent
from app.agents.code_validator import normalize_backend_code
from app.agents.prompts import (
    CODER_CORRECTION_SYSTEM_PROMPT,
    CODER_CORRECTION_USER_PROMPT,
    CODER_SYSTEM_PROMPT,
    CODER_USER_PROMPT,
)

logger = logging.getLogger(__name__)


class CoderAgent(BaseAgent):
    """Writes and fixes FastAPI backend code from a technical blueprint."""

    name = "coder"

    def generate(self, blueprint: str, feature_request: str) -> str:
        code = self._call_llm(
            system=CODER_SYSTEM_PROMPT,
            user=CODER_USER_PROMPT.format(
                feature_request=feature_request,
                blueprint=blueprint,
            ),
            output_format="python",
        )
        return self._normalize_generated_code(code)

    def correct(
        self,
        blueprint: str,
        feature_request: str,
        current_code: str,
        test_logs: str,
    ) -> str:
        code = self._call_llm(
            system=CODER_CORRECTION_SYSTEM_PROMPT,
            user=CODER_CORRECTION_USER_PROMPT.format(
                feature_request=feature_request,
                blueprint=blueprint,
                current_code=current_code,
                test_logs=test_logs,
            ),
            output_format="python",
        )
        return self._normalize_generated_code(code)

    @staticmethod
    def _normalize_generated_code(code: str) -> str:
        """Apply deterministic compatibility fixes for common generated-code drift."""
        report = normalize_backend_code(code)
        for repair in report.repairs:
            logger.info("Applied generated-code repair: %s", repair)
        for issue in report.issues:
            logger.warning("Generated-code validation issue: %s", issue)
        return report.code
