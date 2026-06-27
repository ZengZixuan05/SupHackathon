import json

from app.agents.base import BaseAgent
from app.agents.prompts import FRONTEND_SYSTEM_PROMPT, FRONTEND_USER_PROMPT


class FrontendAgent(BaseAgent):
    """Builds a React/Tailwind UI wired to the deployed OpenAPI endpoints."""

    name = "frontend"

    def generate_ui(
        self,
        blueprint: str,
        openapi_schema: dict,
        api_base_url: str,
    ) -> str:
        return self._call_llm(
            system=FRONTEND_SYSTEM_PROMPT,
            user=FRONTEND_USER_PROMPT.format(
                blueprint=blueprint,
                openapi_schema=json.dumps(openapi_schema, indent=2),
                api_base_url=api_base_url,
            ),
            output_format="html",
            temperature=0.4,
        )
