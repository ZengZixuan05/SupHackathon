You are an expert Principal AI Engineer specialized in Building Agentic DevOps and self-correcting code-execution systems. 

We are building a Proof of Work hackathon prototype: an Autonomous Full-Stack Feature Pipeline. The goal is to build a system where an AI agent writes FastAPI code based on a feature specification, runs it programmatically, captures execution/test errors, and self-corrects until the tests pass.

Implement this complete architecture in a clean, production-ready Python project using FastAPI, Pydantic, and standard Python execution libraries (like `subprocess` or `exec`).

### Project Architecture & Requirements

1. State Management:
   - Create a central state tracker (using a Pydantic model or dataclass) that maintains: 
     - `feature_request`: string
     - `current_code`: string
     - `iteration_count`: int
     - `test_logs`: string
     - `status`: "generating" | "testing" | "correcting" | "success" | "failed"

2. The Code Generation Agent (The Backend Coder):
   - Takes a feature specification (e.g., "A user management system with user registration, login, and profile retrieval via JWT").
   - Generates a standalone, fully valid `main.py` using FastAPI and Pydantic. 
   - Rule: The output must contain ONLY valid Python code. No markdown wrapping (```python) inside the string payload when processed by the agent parser.

3. The Sandbox Execution & QA Engine:
   - Programmatically writes the generated code to a temporary workspace file (e.g., `sandbox_app.py`).
   - Programmatically generates a companion test file (`test_sandbox.py`) using `fastapi.testclient.TestClient` and `pytest` that targets the expected endpoints.
   - Uses Python's `subprocess` module to run `pytest test_sandbox.py`.
   - Captures `stdout`, `stderr`, and the exit code.

4. The Self-Correction Loop:
   - If the pytest exit code is 0, set status to "success" and terminate.
   - If the exit code is non-zero (failure), extract the raw traceback/error log from `stderr`/`stdout`.
   - Increment `iteration_count`. If `iteration_count > 5`, fail gracefully.
   - Pass the `current_code` and the `test_logs` back to the Code Generation Agent with a strict prompt: "Your previous code failed the test suite with the following errors. Identify the root cause (e.g., schema mismatch, syntax error, missing dependency, status code mismatch) and rewrite the code to fix it."

5. Frontend / Dashboard (Optional API):
   - Expose an orchestra API endpoint (`POST /generate-feature`) so we can trigger this whole loop from a frontend UI. The endpoint should stream or return the full execution history (all generation attempts, tracebacks, and final passing code).

### Execution Phase

Let's build this incrementally:
1. First, scaffold the project structure, including the core orchestration script, the LLM prompting layer (use any standard LLM client API like OpenAI or Anthropic SDKs), and the subprocess testing utility.
2. Ensure proper error handling when running the subprocess so the orchestration loop never crashes, even if the generated code contains catastrophic syntax errors.

Generate the foundation files now, keeping the code modular, readable, and highly robust for a live demonstration.