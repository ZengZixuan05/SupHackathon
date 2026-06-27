from app.agents.utils import extract_python_code


def test_extract_python_code_from_fenced_block():
    raw = "```python\nfrom fastapi import FastAPI\napp = FastAPI()\n```"
    assert "from fastapi import FastAPI" in extract_python_code(raw)
    assert "```" not in extract_python_code(raw)


def test_extract_python_code_plain():
    raw = "from fastapi import FastAPI\napp = FastAPI()"
    assert extract_python_code(raw) == raw
