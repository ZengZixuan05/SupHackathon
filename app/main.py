import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.deploy.loader import mount_generated_app, registry
from app.models.state import AgentName, AttemptRecord, PipelineState, PipelineStatus
from app.orchestrator.pipeline import FeaturePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Feature Pipeline",
    description="Multi-agent system: PM → Coder → QA (self-correcting loop) → Frontend → Deploy",
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
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autonomous Feature Pipeline</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }
    h1 { font-size: 1.5rem; }
    .pipeline { display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap; }
    .agent { padding: 0.4rem 0.8rem; border-radius: 999px; background: #f4f4f5; font-size: 0.85rem; }
    .agent.active { background: #2563eb; color: #fff; }
    textarea { width: 100%; min-height: 120px; padding: 0.75rem; font: inherit; border: 1px solid #ccc; border-radius: 6px; }
    button { margin-top: 0.75rem; padding: 0.6rem 1.2rem; font: inherit; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; margin-right: 0.5rem; }
    button:disabled { opacity: 0.6; cursor: wait; }
    button.secondary { background: #71717a; }
    pre { background: #f4f4f5; padding: 1rem; border-radius: 6px; overflow: auto; font-size: 0.82rem; white-space: pre-wrap; max-height: 400px; }
    .links { margin-top: 1.5rem; font-size: 0.9rem; }
    .links a { margin-right: 1rem; }
    #status { margin-top: 1rem; font-weight: 600; }
    #deploy-links { margin-top: 0.75rem; }
    #deploy-links a { display: inline-block; margin-right: 1rem; color: #2563eb; }
    .section { margin-top: 1.5rem; }
    .section h2 { font-size: 1rem; margin-bottom: 0.5rem; }
  </style>
</head>
<body>
  <h1>Autonomous Feature Pipeline</h1>
  <p>Multi-agent system: PM plans → Coder writes → QA tests → self-corrects → Frontend deploys.</p>

  <div class="pipeline">
    <span class="agent" id="a-pm">1. PM Agent</span>
    <span class="agent" id="a-coder">2. Coder Agent</span>
    <span class="agent" id="a-qa">3. QA Agent</span>
    <span class="agent" id="a-fe">4. Frontend Agent</span>
  </div>

  <textarea id="feature" placeholder="Describe a feature or paste markdown spec..."></textarea>
  <br>
  <button id="run">Run Pipeline</button>
  <button class="secondary" id="load-example">Load Example Spec</button>
  <p id="status"></p>
  <div id="deploy-links"></div>

  <div class="section" id="blueprint-section" hidden>
    <h2>Technical Blueprint (PM Agent)</h2>
    <pre id="blueprint"></pre>
  </div>
  <div class="section" id="output-section" hidden>
    <h2>Pipeline Result</h2>
    <pre id="output"></pre>
  </div>

  <div class="links">
    <a href="/docs">Orchestrator API docs</a>
    <a href="/deployments">Deployments</a>
    <a href="/health">Health</a>
  </div>

  <script>
    const agents = { pm: "a-pm", coder: "a-coder", qa: "a-qa", frontend: "a-fe" };
    function setActiveAgent(name) {
      Object.values(agents).forEach(id => document.getElementById(id).classList.remove("active"));
      if (name && agents[name]) document.getElementById(agents[name]).classList.add("active");
    }

    document.getElementById("load-example").addEventListener("click", async () => {
      const res = await fetch("/specs/example");
      document.getElementById("feature").value = await res.text();
    });

    document.getElementById("run").addEventListener("click", async () => {
      const text = document.getElementById("feature").value.trim();
      if (text.length < 10) { alert("Please enter at least 10 characters."); return; }
      const btn = document.getElementById("run");
      btn.disabled = true;
      setActiveAgent("pm");
      document.getElementById("status").textContent = "PM Agent planning…";
      document.getElementById("deploy-links").innerHTML = "";
      document.getElementById("blueprint-section").hidden = true;
      document.getElementById("output-section").hidden = true;

      try {
        const res = await fetch("/generate-feature", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ feature_request: text }),
        });
        const data = await res.json();
        setActiveAgent(data.active_agent);
        document.getElementById("status").textContent =
          "Status: " + data.status + " | Iterations: " + data.iteration_count;

        if (data.technical_blueprint) {
          document.getElementById("blueprint").textContent = data.technical_blueprint;
          document.getElementById("blueprint-section").hidden = false;
        }

        if (data.status === "success") {
          setActiveAgent("frontend");
          document.getElementById("deploy-links").innerHTML =
            '<a href="' + data.live_api_path + '/docs" target="_blank">Live Swagger UI</a>' +
            '<a href="' + data.live_ui_path + '" target="_blank">Generated React UI</a>';
        }

        document.getElementById("output").textContent = JSON.stringify(data, null, 2);
        document.getElementById("output-section").hidden = false;
      } catch (e) {
        document.getElementById("status").textContent = "Request failed.";
      } finally {
        btn.disabled = false;
      }
    });
  </script>
</body>
</html>"""


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
    )
