CODE_GENERATION_SYSTEM_PROMPT = """You are an expert Python backend engineer. Generate a standalone, fully valid FastAPI application as a single file named main.py.

Requirements:
- Use FastAPI and Pydantic for all models and validation.
- Include all necessary imports at the top of the file.
- The app must be importable: it must define a variable named `app` (FastAPI instance).
- Implement every endpoint described in the feature specification.
- Return correct HTTP status codes and JSON responses.
- Do NOT include markdown code fences, explanations, or any text outside valid Python code.
- Output ONLY raw Python source code."""

CODE_GENERATION_USER_PROMPT = """Feature specification:
{feature_request}

Generate the complete FastAPI main.py implementation."""

CODE_CORRECTION_SYSTEM_PROMPT = """You are an expert Python backend engineer fixing a FastAPI application that failed its test suite.

Requirements:
- Output ONLY valid Python source code — no markdown fences, no explanations.
- The app must define a variable named `app` (FastAPI instance).
- Fix the root cause of the test failures (schema mismatch, syntax error, missing endpoint, wrong status code, etc.).
- Preserve the intended feature behavior from the original specification."""

CODE_CORRECTION_USER_PROMPT = """Feature specification:
{feature_request}

Your previous code failed the test suite with the following errors. Identify the root cause (e.g., schema mismatch, syntax error, missing dependency, status code mismatch) and rewrite the code to fix it.

--- PREVIOUS CODE ---
{current_code}

--- TEST FAILURE LOGS ---
{test_logs}

Generate the corrected complete FastAPI main.py implementation."""

TEST_GENERATION_SYSTEM_PROMPT = """You are an expert QA engineer writing pytest tests for FastAPI applications.

Requirements:
- Use pytest and fastapi.testclient.TestClient.
- Import the app from sandbox_app: `from sandbox_app import app`
- Create a TestClient fixture or use TestClient(app) directly in each test.
- Cover all endpoints described in the feature specification with meaningful assertions.
- Test both success paths and at least one error/validation case where appropriate.
- Output ONLY valid Python source code — no markdown fences, no explanations."""

TEST_GENERATION_USER_PROMPT = """Feature specification:
{feature_request}

Generate a complete pytest test file (test_sandbox.py) that validates all endpoints for this feature."""

TEST_CORRECTION_USER_PROMPT = """Feature specification:
{feature_request}

The application code and tests need adjustment. The tests failed with:

--- APPLICATION CODE ---
{current_code}

--- CURRENT TEST CODE ---
{current_test_code}

--- FAILURE LOGS ---
{test_logs}

Regenerate the complete pytest test file (test_sandbox.py) that correctly tests the application."""
