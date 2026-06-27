import logging

from app.agents.code_generator import CodeGenerator
from app.agents.test_generator import TestGenerator
from app.config import settings
from app.models.state import AttemptRecord, PipelineState, PipelineStatus
from app.sandbox.executor import SandboxExecutor

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """Orchestrates code generation, sandbox testing, and self-correction."""

    def __init__(self) -> None:
        self._code_generator = CodeGenerator()
        self._test_generator = TestGenerator()
        self._sandbox = SandboxExecutor()
        self._max_iterations = settings.max_iterations

    def run(self, feature_request: str) -> PipelineState:
        state = PipelineState(feature_request=feature_request, status=PipelineStatus.GENERATING)

        try:
            state.status = PipelineStatus.GENERATING
            state.current_code = self._code_generator.generate(feature_request)
            state.current_test_code = self._test_generator.generate(feature_request)
        except Exception as exc:
            state.status = PipelineStatus.FAILED
            state.test_logs = f"Initial generation failed: {exc}"
            state.add_attempt(
                AttemptRecord(
                    iteration=0,
                    status=PipelineStatus.FAILED,
                    code=state.current_code,
                    test_code=state.current_test_code,
                    test_logs=state.test_logs,
                )
            )
            return state

        while True:
            state.status = PipelineStatus.TESTING
            result = self._sandbox.run_tests(state.current_code, state.current_test_code)
            state.test_logs = result.combined_logs

            attempt = AttemptRecord(
                iteration=state.iteration_count,
                status=PipelineStatus.TESTING,
                code=state.current_code,
                test_code=state.current_test_code,
                test_logs=state.test_logs,
                exit_code=result.exit_code,
            )

            if result.exit_code == 0:
                state.status = PipelineStatus.SUCCESS
                attempt.status = PipelineStatus.SUCCESS
                state.add_attempt(attempt)
                return state

            state.add_attempt(attempt)
            state.iteration_count += 1

            if state.iteration_count > self._max_iterations:
                state.status = PipelineStatus.FAILED
                state.test_logs = (
                    f"Exceeded maximum iterations ({self._max_iterations}).\n\n{state.test_logs}"
                )
                return state

            state.status = PipelineStatus.CORRECTING
            try:
                state.current_code = self._code_generator.correct(
                    feature_request=feature_request,
                    current_code=state.current_code,
                    test_logs=result.combined_logs,
                )
            except Exception as exc:
                state.status = PipelineStatus.FAILED
                state.test_logs = f"Correction failed: {exc}\n\n{result.combined_logs}"
                logger.exception("Code correction failed")
                return state
