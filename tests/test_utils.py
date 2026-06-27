from app.agents.coder_agent import CoderAgent
from app.agents.utils import extract_html, extract_python_code


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
