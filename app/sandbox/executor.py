import logging
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

APP_FILENAME = "sandbox_app.py"
TEST_FILENAME = "test_sandbox.py"


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    combined_logs: str
    workspace: Path


class SandboxExecutor:
    """Writes generated code to a temp workspace and runs pytest."""

    def run_tests(self, app_code: str, test_code: str) -> SandboxResult:
        with tempfile.TemporaryDirectory(prefix="feature_pipeline_") as tmp:
            workspace = Path(tmp)
            self._write_files(workspace, app_code, test_code)
            return self._execute_pytest(workspace)

    def _write_files(self, workspace: Path, app_code: str, test_code: str) -> None:
        (workspace / APP_FILENAME).write_text(app_code, encoding="utf-8")
        (workspace / TEST_FILENAME).write_text(test_code, encoding="utf-8")

    def _execute_pytest(self, workspace: Path) -> SandboxResult:
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            TEST_FILENAME,
            "-v",
            "--tb=short",
            "-p",
            "no:cacheprovider",
        ]

        stdout = ""
        stderr = ""
        exit_code = 1

        try:
            result = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=120,
                env=self._build_env(workspace),
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            exit_code = result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + "\n[TIMEOUT] pytest exceeded 120s limit."
            exit_code = 124
            logger.warning("pytest timed out in sandbox")
        except Exception as exc:
            stderr = f"[ORCHESTRATOR ERROR] Failed to run pytest: {exc}"
            exit_code = 1
            logger.exception("Subprocess execution failed")

        combined = self._combine_logs(stdout, stderr)
        return SandboxResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            combined_logs=combined,
            workspace=workspace,
        )

    def _build_env(self, workspace: Path) -> dict:
        import os

        env = os.environ.copy()
        env["PYTHONPATH"] = str(workspace)
        return env

    def _combine_logs(self, stdout: str, stderr: str) -> str:
        parts = []
        if stdout.strip():
            parts.append("=== STDOUT ===\n" + stdout.strip())
        if stderr.strip():
            parts.append("=== STDERR ===\n" + stderr.strip())
        return "\n\n".join(parts) if parts else "No output captured."
