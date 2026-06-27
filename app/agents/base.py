import logging
from typing import Literal

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

OutputFormat = Literal["text", "python", "html"]


class BaseAgent:
    """Shared LLM client wrapper for all pipeline agents."""

    name: str = "base"

    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key or None)
        self._model = settings.openai_model

    def _call_llm(
        self,
        system: str,
        user: str,
        *,
        output_format: OutputFormat = "text",
        temperature: float = 0.2,
    ) -> str:
        from app.agents.utils import extract_html, extract_python_code

        logger.info("%s agent calling model %s for %s output", self.name, self._model, output_format)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
            )
            raw = response.choices[0].message.content or ""
            logger.info("%s agent received %d chars from model", self.name, len(raw))
        except Exception as exc:
            logger.exception("%s agent LLM call failed", self.name)
            raise RuntimeError(f"{self.name} agent failed: {exc}") from exc

        if output_format == "python":
            return extract_python_code(raw)
        if output_format == "html":
            return extract_html(raw)
        return raw.strip()
