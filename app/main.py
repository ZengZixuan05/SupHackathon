import logging
from typing import List

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
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
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }
    h1 { font-size: 1.5rem; }
    textarea { width: 100%; min-height: 100px; padding: 0.75rem; font: inherit; border: 1px solid #ccc; border-radius: 6px; }
    button { margin-top: 0.75rem; padding: 0.6rem 1.2rem; font: inherit; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; }
    button:disabled { opacity: 0.6; cursor: wait; }
    pre { background: #f4f4f5; padding: 1rem; border-radius: 6px; overflow: auto; font-size: 0.85rem; white-space: pre-wrap; }
    .links { margin-top: 1.5rem; font-size: 0.9rem; }
    .links a { margin-right: 1rem; }
    #status { margin-top: 1rem; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Autonomous Feature Pipeline</h1>
  <p>Describe a FastAPI feature. The agent will generate code, run pytest, and self-correct until tests pass.</p>
  <textarea id="feature" placeholder="e.g. A todo API with create, list, and delete endpoints"></textarea>
  <br>
  <button id="run">Generate Feature</button>
  <p id="status"></p>
  <pre id="output" hidden></pre>
  <div class="links">
    <a href="/docs">API docs</a>
    <a href="/health">Health check</a>
  </div>
  <script>
    const btn = document.getElementById("run");
    const feature = document.getElementById("feature");
    const status = document.getElementById("status");
    const output = document.getElementById("output");

    btn.addEventListener("click", async () => {
      const text = feature.value.trim();
      if (text.length < 10) { alert("Please enter at least 10 characters."); return; }
      btn.disabled = true;
      status.textContent = "Running pipeline…";
      output.hidden = true;
      try {
        const res = await fetch("/generate-feature", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ feature_request: text }),
        });
        const data = await res.json();
        status.textContent = "Status: " + data.status + " (iterations: " + data.iteration_count + ")";
        output.textContent = JSON.stringify(data, null, 2);
        output.hidden = false;
      } catch (e) {
        status.textContent = "Request failed.";
        output.textContent = String(e);
        output.hidden = false;
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
