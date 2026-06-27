from app.agents.base import BaseAgent
from app.agents.prompts import PM_SYSTEM_PROMPT, PM_USER_PROMPT


class PMAgent(BaseAgent):
    """Turns a product feature request into a technical blueprint for engineering."""

    name = "pm"

    def create_blueprint(self, feature_request: str) -> str:
        return self._call_llm(
            system=PM_SYSTEM_PROMPT,
            user=PM_USER_PROMPT.format(feature_request=feature_request),
            output_format="text",
            temperature=0.3,
        )
