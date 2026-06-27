from app.sandbox.executor import SandboxExecutor


def test_sandbox_handles_syntax_error():
    executor = SandboxExecutor()
    result = executor.run_tests("def broken(", "from sandbox_app import app")
    assert result.exit_code != 0
    assert len(result.combined_logs) > 0


def test_sandbox_passes_valid_app():
    executor = SandboxExecutor()
    app_code = (
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/')\n"
        "def root(): return {'ok': True}\n"
    )
    test_code = (
        "from fastapi.testclient import TestClient\n"
        "from sandbox_app import app\n"
        "client = TestClient(app)\n"
        "def test_root(): assert client.get('/').status_code == 200\n"
    )
    result = executor.run_tests(app_code, test_code)
    assert result.exit_code == 0
