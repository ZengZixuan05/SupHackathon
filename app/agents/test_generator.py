import logging

from openai import OpenAI

from app.agents.prompts import (
    TEST_CORRECTION_USER_PROMPT,
    TEST_GENERATION_SYSTEM_PROMPT,
    TEST_GENERATION_USER_PROMPT,
)
from app.agents.utils import extract_python_code
from app.config import settings

logger = logging.getLogger(__name__)


class TestGenerator:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key or None)
        self._model = settings.openai_model

    def generate(self, feature_request: str) -> str:
        return self._call_llm(
            system=TEST_GENERATION_SYSTEM_PROMPT,
            user=TEST_GENERATION_USER_PROMPT.format(feature_request=feature_request),
        )

    def correct(
        self,
        feature_request: str,
        current_code: str,
        current_test_code: str,
        test_logs: str,
    ) -> str:
        return self._call_llm(
            system=TEST_GENERATION_SYSTEM_PROMPT,
            user=TEST_CORRECTION_USER_PROMPT.format(
                feature_request=feature_request,
                current_code=current_code,
                current_test_code=current_test_code,
                test_logs=test_logs,
            ),
        )

    def _call_llm(self, system: str, user: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            return extract_python_code(raw)
        except Exception as exc:
            logger.exception("Test generation LLM call failed")
            raise RuntimeError(f"Test generation failed: {exc}") from exc
