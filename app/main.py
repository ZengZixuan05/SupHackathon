import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.deploy.loader import mount_generated_app, registry
from app.homepage import HOME_PAGE_HTML
from app.models.state import AgentName, AttemptRecord, PipelineState, PipelineStatus
from app.orchestrator.pipeline import FeaturePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Feature Pipeline",
    description="Multi-agent system: PM to Coder to QA to Frontend to Deploy",
    version="0.2.0",
)

SPECS_DIR = Path("specs")


class GenerateFeatureRequest(BaseModel):
    feature_request: str = Field(
        ...,
        min_length=10,
        description="Natural language or markdown feature specification.",
    )


class GenerateFeatureResponse(BaseModel):
    run_id: str
    feature_request: str
    technical_blueprint: str
    status: PipelineStatus
    active_agent: AgentName | None
    iteration_count: int
    final_code: str
    final_test_code: str
    frontend_code: str
    openapi_schema: Dict[str, Any] | None
    live_api_path: str | None
    live_ui_path: str | None
    test_logs: str
    history: List[AttemptRecord]
    event_log: List[str]


class DeploymentSummary(BaseModel):
    deployment_id: str
    feature_request: str
    live_api_path: str
    live_ui_path: str


@app.on_event("startup")
def remount_saved_deployments() -> None:
    for deployment in registry.list_all():
        try:
            mount_generated_app(app, deployment.deployment_id, deployment.backend_code)
            logger.info("Re-mounted deployment %s", deployment.deployment_id)
        except Exception as exc:
            logger.warning("Could not remount %s: %s", deployment.deployment_id, exc)


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return HOME_PAGE_HTML


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "deployments": len(registry.list_all())}


@app.get("/specs/example")
def example_spec() -> Response:
    path = SPECS_DIR / "example_inventory.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Example spec not found")
    return Response(content=path.read_text(encoding="utf-8"), media_type="text/markdown")


@app.get("/deployments", response_model=List[DeploymentSummary])
def list_deployments() -> List[DeploymentSummary]:
    return [
        DeploymentSummary(
            deployment_id=d.deployment_id,
            feature_request=d.feature_request[:120],
            live_api_path=d.api_mount_path,
            live_ui_path=d.ui_path,
        )
        for d in registry.list_all()
    ]


@app.get("/ui/{deployment_id}", response_class=HTMLResponse)
def serve_generated_ui(deployment_id: str) -> str:
    deployment = registry.get(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment.frontend_html


@app.post("/generate-feature", response_model=GenerateFeatureResponse)
def generate_feature(body: GenerateFeatureRequest) -> GenerateFeatureResponse:
    logger.info("Starting multi-agent pipeline: %s", body.feature_request[:80])

    pipeline = FeaturePipeline()
    try:
        state: PipelineState = pipeline.run(body.feature_request)
    except Exception as exc:
        logger.exception("Pipeline crashed unexpectedly")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc

    if state.status == PipelineStatus.SUCCESS and state.deployment_id:
        try:
            mount_generated_app(app, state.deployment_id, state.current_code)
        except Exception as exc:
            logger.warning("Could not mount live API: %s", exc)

    return GenerateFeatureResponse(
        run_id=state.run_id,
        feature_request=state.feature_request,
        technical_blueprint=state.technical_blueprint,
        status=state.status,
        active_agent=state.active_agent,
        iteration_count=state.iteration_count,
        final_code=state.current_code,
        final_test_code=state.current_test_code,
        frontend_code=state.frontend_code,
        openapi_schema=state.openapi_schema,
        live_api_path=state.live_api_path,
        live_ui_path=state.live_ui_path,
        test_logs=state.test_logs,
        history=state.history,
        event_log=state.event_log,
    )
