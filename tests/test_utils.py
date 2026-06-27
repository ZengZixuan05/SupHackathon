from app.agents.coder_agent import CoderAgent
from app.agents.code_validator import find_backend_code_issues, normalize_backend_code
from app.agents.utils import extract_html, extract_json_object, extract_python_code


def test_extract_python_code_from_fenced_block():
    raw = "```python\nfrom fastapi import FastAPI\napp = FastAPI()\n```"
    assert "from fastapi import FastAPI" in extract_python_code(raw)
    assert "```" not in extract_python_code(raw)


def test_extract_python_code_plain():
    raw = "from fastapi import FastAPI\napp = FastAPI()"
    assert extract_python_code(raw) == raw


def test_extract_html_from_fenced_block():
    raw = "```html\n<!DOCTYPE html><html><body>Hi</body></html>\n```"
    result = extract_html(raw)
    assert result.startswith("<!DOCTYPE html>")
    assert "```" not in result


def test_extract_html_plain():
    raw = "<!DOCTYPE html><html><body>Hi</body></html>"
    assert extract_html(raw) == raw


def test_coder_normalizes_pydantic_v2_regex_keyword():
    raw = "email: constr(regex=r'^[^@]+@[^@]+$')"
    assert CoderAgent._normalize_generated_code(raw) == (
        "email: constr(pattern=r'^[^@]+@[^@]+$')"
    )


def test_extract_json_object_from_fenced_block():
    raw = "```json\n{\"summary\":\"ok\"}\n```"
    assert extract_json_object(raw) == '{"summary":"ok"}'


def test_backend_validator_repairs_emailstr_and_reports_response_model_dict():
    code = (
        "from pydantic import BaseModel, EmailStr\n"
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "class User(BaseModel):\n"
        "    email: EmailStr\n"
        "@app.post('/users', response_model=dict)\n"
        "def create_user(user: User): return {'email': user.email}\n"
    )
    report = normalize_backend_code(code)
    assert "EmailStr" not in report.code
    assert any("email-validator" in repair for repair in report.repairs)
    assert any("response_model=dict" in issue for issue in report.issues)


def test_backend_validator_finds_routes_missing_response_model():
    code = "from fastapi import FastAPI\napp=FastAPI()\n@app.get('/ping')\ndef ping(): return {}"
    assert find_backend_code_issues(code) == ["Routes missing explicit response_model: GET /ping"]
