import json
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ContractField(BaseModel):
    name: str
    type: str = "str"
    required: bool = True
    validation: str = ""
    description: str = ""


class ContractEntity(BaseModel):
    name: str
    description: str = ""
    storage: str = ""
    fields: List[ContractField] = Field(default_factory=list)


class ContractEndpoint(BaseModel):
    method: str
    path: str
    purpose: str = ""
    request_model: str | None = None
    response_model: str
    success_status: int = 200
    error_statuses: Dict[str, int] = Field(default_factory=dict)
    business_rules: List[str] = Field(default_factory=list)


class ContractTestCase(BaseModel):
    name: str
    scenario: str
    endpoint: str
    expected_status: int
    setup: List[str] = Field(default_factory=list)
    assertions: List[str] = Field(default_factory=list)


class FeatureContract(BaseModel):
    summary: str
    domain: str = "generic"
    entities: List[ContractEntity] = Field(default_factory=list)
    endpoints: List[ContractEndpoint] = Field(default_factory=list)
    business_rules: List[str] = Field(default_factory=list)
    test_cases: List[ContractTestCase] = Field(default_factory=list)
    data_stores: List[str] = Field(default_factory=list)
    non_goals: List[str] = Field(default_factory=list)

    def to_pretty_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=2)

    def to_prompt_text(self) -> str:
        return self.to_pretty_json()

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
