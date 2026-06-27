from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.agents.prompts import PM_SYSTEM_PROMPT, PM_USER_PROMPT
from app.agents.utils import extract_json_object
from app.models.contract import FeatureContract


class PMAgent(BaseAgent):
    """Turns a product feature request into a technical blueprint for engineering."""

    name = "pm"

    def create_contract(self, feature_request: str) -> FeatureContract:
        raw = self._call_llm(
            system=PM_SYSTEM_PROMPT,
            user=PM_USER_PROMPT.format(feature_request=feature_request),
            output_format="text",
            temperature=0.3,
        )
        try:
            return FeatureContract.model_validate_json(extract_json_object(raw))
        except ValidationError as exc:
            raise RuntimeError(f"PM contract was not valid JSON: {exc}") from exc

    def create_blueprint(self, feature_request: str) -> str:
        return self.create_contract(feature_request).to_prompt_text()
