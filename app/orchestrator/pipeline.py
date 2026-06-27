import logging

from app.agents.coder_agent import CoderAgent
from app.agents.frontend_agent import FrontendAgent
from app.agents.pm_agent import PMAgent
from app.agents.qa_agent import QAAgent
from app.config import settings
from app.deploy.loader import (
    Deployment,
    create_run_id,
    extract_openapi,
    load_fastapi_app,
    registry,
    save_artifacts,
)
from app.models.state import AgentName, AttemptRecord, PipelineState, PipelineStatus

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """
    Multi-agent orchestrator:
      PM Agent → Coder Agent → QA Agent (loop) → Frontend Agent → Deploy
    """

    def __init__(self) -> None:
        self._pm = PMAgent()
        self._coder = CoderAgent()
        self._qa = QAAgent()
        self._frontend = FrontendAgent()
        self._max_iterations = settings.max_iterations

    def run(self, feature_request: str) -> PipelineState:
        run_id = create_run_id()
        state = PipelineState(
            run_id=run_id,
            feature_request=feature_request,
            status=PipelineStatus.PLANNING,
            active_agent=AgentName.PM,
        )

        # ── Agent 1: PM ──────────────────────────────────────────────
        try:
            state.technical_blueprint = self._pm.create_blueprint(feature_request)
            logger.info("[%s] PM Agent produced blueprint (%d chars)", run_id, len(state.technical_blueprint))
        except Exception as exc:
            return self._fail(state, f"PM Agent failed: {exc}", AgentName.PM)

        blueprint = state.technical_blueprint

        # ── Agent 2: Coder (initial) + Agent 3: QA (initial tests) ──
        state.status = PipelineStatus.GENERATING
        state.active_agent = AgentName.CODER
        try:
            state.current_code = self._coder.generate(blueprint, feature_request)
        except Exception as exc:
            return self._fail(state, f"Coder Agent failed: {exc}", AgentName.CODER)

        state.active_agent = AgentName.QA
        try:
            state.current_test_code = self._qa.generate_tests(blueprint, feature_request)
        except Exception as exc:
            return self._fail(state, f"QA Agent test generation failed: {exc}", AgentName.QA)

        # ── Self-correction loop ─────────────────────────────────────
        while True:
            state.status = PipelineStatus.TESTING
            state.active_agent = AgentName.QA
            result = self._qa.run_tests(state.current_code, state.current_test_code)
            state.test_logs = result.combined_logs

            attempt = AttemptRecord(
                iteration=state.iteration_count,
                status=PipelineStatus.TESTING,
                agent=AgentName.QA,
                code=state.current_code,
                test_code=state.current_test_code,
                test_logs=state.test_logs,
                exit_code=result.exit_code,
            )

            if result.exit_code == 0:
                attempt.status = PipelineStatus.SUCCESS
                state.add_attempt(attempt)
                break

            state.add_attempt(attempt)
            state.iteration_count += 1

            if state.iteration_count > self._max_iterations:
                state.status = PipelineStatus.FAILED
                state.test_logs = (
                    f"Exceeded maximum iterations ({self._max_iterations}).\n\n{state.test_logs}"
                )
                return state

            # Feed traceback back to Coder Agent
            state.status = PipelineStatus.CORRECTING
            state.active_agent = AgentName.CODER
            try:
                state.current_code = self._coder.correct(
                    blueprint=blueprint,
                    feature_request=feature_request,
                    current_code=state.current_code,
                    test_logs=result.combined_logs,
                )
            except Exception as exc:
                state.status = PipelineStatus.FAILED
                state.test_logs = f"Coder correction failed: {exc}\n\n{result.combined_logs}"
                logger.exception("Coder correction failed")
                return state

        # ── Tests passed: extract OpenAPI, build UI, deploy ──────────
        state.status = PipelineStatus.BUILDING_UI
        try:
            app_instance = load_fastapi_app(state.current_code, module_name=f"preview_{run_id}")
            state.openapi_schema = extract_openapi(app_instance)
        except Exception as exc:
            logger.warning("OpenAPI extraction failed: %s", exc)
            state.openapi_schema = {}

        api_base = f"/live/{run_id}"
        state.active_agent = AgentName.FRONTEND
        try:
            state.frontend_code = self._frontend.generate_ui(
                blueprint=blueprint,
                openapi_schema=state.openapi_schema or {},
                api_base_url=api_base,
            )
        except Exception as exc:
            logger.warning("Frontend Agent failed (non-fatal): %s", exc)
            state.frontend_code = self._fallback_ui(api_base)

        state.status = PipelineStatus.DEPLOYING
        workspace = save_artifacts(
            run_id,
            state.current_code,
            state.current_test_code,
            state.frontend_code,
        )

        deployment = Deployment(
            deployment_id=run_id,
            feature_request=feature_request,
            blueprint=blueprint,
            backend_code=state.current_code,
            test_code=state.current_test_code,
            frontend_html=state.frontend_code,
            openapi_schema=state.openapi_schema or {},
            api_mount_path=api_base,
            ui_path=f"/ui/{run_id}",
            workspace=workspace,
        )
        registry.register(deployment)

        state.deployment_id = run_id
        state.live_api_path = api_base
        state.live_ui_path = deployment.ui_path
        state.status = PipelineStatus.SUCCESS
        state.active_agent = None
        return state

    def _fail(self, state: PipelineState, message: str, agent: AgentName) -> PipelineState:
        state.status = PipelineStatus.FAILED
        state.test_logs = message
        state.active_agent = agent
        state.add_attempt(
            AttemptRecord(
                iteration=state.iteration_count,
                status=PipelineStatus.FAILED,
                agent=agent,
                test_logs=message,
            )
        )
        return state

    def _fallback_ui(self, api_base: str) -> str:
        return f"""<!DOCTYPE html>
<html><head><title>Generated API</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="p-8 font-sans">
<h1 class="text-2xl font-bold mb-4">API Ready</h1>
<p>Explore the live Swagger docs at <a class="text-blue-600 underline" href="{api_base}/docs">{api_base}/docs</a></p>
</body></html>"""
