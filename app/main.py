import logging
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.models.state import AttemptRecord, PipelineState, PipelineStatus
from app.orchestrator.pipeline import FeaturePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Feature Pipeline",
    description="AI agent that generates FastAPI features, tests them, and self-corrects until tests pass.",
    version="0.1.0",
)


class GenerateFeatureRequest(BaseModel):
    feature_request: str = Field(
        ...,
        min_length=10,
        description="Natural language description of the feature to build.",
        examples=[
            "A user management system with user registration, login, and profile retrieval via JWT."
        ],
    )


class GenerateFeatureResponse(BaseModel):
    feature_request: str
    status: PipelineStatus
    iteration_count: int
    final_code: str
    final_test_code: str
    test_logs: str
    history: List[AttemptRecord]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate-feature", response_model=GenerateFeatureResponse)
def generate_feature(body: GenerateFeatureRequest) -> GenerateFeatureResponse:
    logger.info("Starting pipeline for feature: %s", body.feature_request[:80])

    pipeline = FeaturePipeline()
    try:
        state: PipelineState = pipeline.run(body.feature_request)
    except Exception as exc:
        logger.exception("Pipeline crashed unexpectedly")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc

    return GenerateFeatureResponse(
        feature_request=state.feature_request,
        status=state.status,
        iteration_count=state.iteration_count,
        final_code=state.current_code,
        final_test_code=state.current_test_code,
        test_logs=state.test_logs,
        history=state.history,
    )
