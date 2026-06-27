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
        self._record(state, "Pipeline started")

        # ── Agent 1: PM ──────────────────────────────────────────────
        try:
            self._record(state, "PM Agent producing structured contract")
            contract = self._pm.create_contract(feature_request)
            state.technical_contract = contract.as_dict()
            state.technical_blueprint = contract.to_prompt_text()
            self._record(
                state,
                (
                    "PM Agent produced contract "
                    f"({len(contract.endpoints)} endpoints, {len(contract.test_cases)} tests)"
                ),
            )
        except Exception as exc:
            return self._fail(state, f"PM Agent failed: {exc}", AgentName.PM)

        blueprint = state.technical_blueprint

        # ── Agent 2: Coder (initial) + Agent 3: QA (initial tests) ──
        state.status = PipelineStatus.GENERATING
        state.active_agent = AgentName.CODER
        try:
            self._record(state, "Coder Agent generating FastAPI app")
            state.current_code = self._coder.generate(blueprint, feature_request)
            self._record(state, f"Coder Agent generated app code ({len(state.current_code)} chars)")
        except Exception as exc:
            return self._fail(state, f"Coder Agent failed: {exc}", AgentName.CODER)

        state.active_agent = AgentName.QA
        try:
            self._record(state, "QA Agent generating pytest suite")
            state.current_test_code = self._qa.generate_tests(blueprint, feature_request)
            self._record(
                state,
                f"QA Agent generated tests ({len(state.current_test_code)} chars)",
            )
        except Exception as exc:
            return self._fail(state, f"QA Agent test generation failed: {exc}", AgentName.QA)

        # ── Self-correction loop ─────────────────────────────────────
        while True:
            state.status = PipelineStatus.TESTING
            state.active_agent = AgentName.QA
            self._record(state, f"QA Agent running pytest iteration {state.iteration_count}")
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
                self._record(state, f"QA passed iteration {state.iteration_count}")
                break

            state.add_attempt(attempt)
            self._record(
                state,
                f"QA failed iteration {state.iteration_count} with exit code {result.exit_code}",
                logging.WARNING,
            )
            debug_path = self._save_attempt_debug(state, result.combined_logs)
            if debug_path:
                self._record(
                    state,
                    f"Saved failing attempt artifacts to {debug_path}",
                    logging.WARNING,
                )
            logger.warning(
                "[%s] QA failure log tail:\n%s",
                state.run_id,
                self._tail(result.combined_logs),
            )
            state.iteration_count += 1

            if state.iteration_count >= self._max_iterations:
                state.status = PipelineStatus.FAILED
                state.test_logs = (
                    f"Exceeded maximum iterations ({self._max_iterations}).\n\n{state.test_logs}"
                )
                self._record(
                    state,
                    f"Stopping after {self._max_iterations} correction rounds",
                    logging.WARNING,
                )
                save_artifacts(
                    run_id,
                    state.current_code,
                    state.current_test_code,
                )
                return state

            logs = result.combined_logs
            is_test_mismatch = self._looks_like_test_mismatch(logs)

            # Fix tests only when the test suite itself is invalid. Assertion failures preserve
            # the contract and should be fixed in application code.
            if is_test_mismatch:
                state.status = PipelineStatus.CORRECTING
                state.active_agent = AgentName.QA
                try:
                    self._record(state, "QA Agent syncing tests to match app code")
                    state.current_test_code = self._qa.sync_tests(
                        blueprint=blueprint,
                        feature_request=feature_request,
                        current_code=state.current_code,
                        test_logs=logs,
                    )
                    self._record(
                        state,
                        f"QA Agent regenerated tests ({len(state.current_test_code)} chars)",
                    )
                except Exception as exc:
                    self._record(
                        state,
                        f"QA test sync failed, falling back to Coder: {exc}",
                        logging.WARNING,
                    )
                    is_test_mismatch = False

            if not is_test_mismatch:
                state.status = PipelineStatus.CORRECTING
                state.active_agent = AgentName.CODER
                try:
                    self._record(state, "Coder Agent correcting app code")
                    state.current_code = self._coder.correct(
                        blueprint=blueprint,
                        feature_request=feature_request,
                        current_code=state.current_code,
                        test_logs=logs,
                    )
                    self._record(
                        state,
                        f"Coder Agent corrected app code ({len(state.current_code)} chars)",
                    )
                except Exception as exc:
                    state.status = PipelineStatus.FAILED
                    state.test_logs = f"Coder correction failed: {exc}\n\n{logs}"
                    self._record(state, f"Coder correction failed: {exc}", logging.ERROR)
                    return state

        # ── Tests passed: extract OpenAPI, build UI, deploy ──────────
        state.status = PipelineStatus.BUILDING_UI
        try:
            self._record(state, "Extracting OpenAPI schema from generated app")
            app_instance = load_fastapi_app(state.current_code, module_name=f"preview_{run_id}")
            state.openapi_schema = extract_openapi(app_instance)
            self._record(
                state,
                f"OpenAPI schema extracted ({len(state.openapi_schema.get('paths', {}))} paths)",
            )
        except Exception as exc:
            self._record(state, f"OpenAPI extraction failed: {exc}", logging.WARNING)
            state.openapi_schema = {}

        api_base = f"/live/{run_id}"
        state.active_agent = AgentName.FRONTEND
        try:
            self._record(state, "Frontend Agent generating demo UI")
            state.frontend_code = self._frontend.generate_ui(
                blueprint=blueprint,
                openapi_schema=state.openapi_schema or {},
                api_base_url=api_base,
            )
            self._record(state, f"Frontend Agent generated UI ({len(state.frontend_code)} chars)")
        except Exception as exc:
            self._record(
                state,
                f"Frontend Agent failed; using fallback UI: {exc}",
                logging.WARNING,
            )
            state.frontend_code = self._fallback_ui(api_base)

        state.status = PipelineStatus.DEPLOYING
        self._record(state, "Saving generated artifacts")
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
        self._record(state, f"Deployment ready at {deployment.ui_path}")
        return state

    def _fail(self, state: PipelineState, message: str, agent: AgentName) -> PipelineState:
        state.status = PipelineStatus.FAILED
        state.test_logs = message
        state.active_agent = agent
        self._record(state, message, logging.ERROR)
        state.add_attempt(
            AttemptRecord(
                iteration=state.iteration_count,
                status=PipelineStatus.FAILED,
                agent=agent,
                test_logs=message,
            )
        )
        return state

    def _record(
        self,
        state: PipelineState,
        message: str,
        level: int = logging.INFO,
    ) -> None:
        state.add_event(message)
        logger.log(level, "[%s] %s", state.run_id, message)

    def _save_attempt_debug(self, state: PipelineState, logs: str) -> str:
        try:
            workspace = (
                settings.generated_dir
                / state.run_id
                / "attempts"
                / f"iteration_{state.iteration_count}"
            )
            workspace.mkdir(parents=True, exist_ok=True)
            (workspace / "sandbox_app.py.txt").write_text(state.current_code, encoding="utf-8")
            (workspace / "test_sandbox.py.txt").write_text(
                state.current_test_code,
                encoding="utf-8",
            )
            (workspace / "pytest.log").write_text(logs, encoding="utf-8")
            return str(workspace)
        except Exception as exc:
            logger.warning("[%s] Could not save attempt debug artifacts: %s", state.run_id, exc)
            return ""

    def _tail(self, text: str, max_chars: int = 4000) -> str:
        if len(text) <= max_chars:
            return text
        return "... truncated ...\n" + text[-max_chars:]

    def _looks_like_test_mismatch(self, logs: str) -> bool:
        """Heuristic: regenerate tests only when the test suite itself is broken."""
        indicators = (
            "SyntaxError",
            "IndentationError",
            "fixture ",
            "NameError",
            "ImportError while importing test module",
            "ModuleNotFoundError: No module named 'pytest'",
        )
        return any(marker in logs for marker in indicators) and "sandbox_app.py" not in logs

    def _fallback_ui(self, api_base: str) -> str:
        return f"""<!DOCTYPE html>
<html><head><title>Generated API</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="p-8 font-sans">
<h1 class="text-2xl font-bold mb-4">API Ready</h1>
<p>Explore the live Swagger docs at <a class="text-blue-600 underline" href="{api_base}/docs">{api_base}/docs</a></p>
</body></html>"""
