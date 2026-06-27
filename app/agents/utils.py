import re


def extract_python_code(raw: str) -> str:
    """Strip markdown fences and surrounding prose from LLM output."""
    text = raw.strip()

    fence_pattern = r"```(?:python)?\s*\n?(.*?)```"
    matches = re.findall(fence_pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()

    return text
