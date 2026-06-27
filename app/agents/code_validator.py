import re
from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    code: str
    issues: list[str] = field(default_factory=list)
    repairs: list[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)


def normalize_backend_code(code: str) -> ValidationReport:
    """Apply deterministic repairs and report common generated FastAPI problems."""
    report = ValidationReport(code=code)
    normalized = code

    if re.search(r"constr\(\s*regex\s*=", normalized):
        normalized = re.sub(r"constr\(\s*regex\s*=", "constr(pattern=", normalized)
        report.repairs.append("Replaced Pydantic v1 constr(regex=...) with constr(pattern=...).")

    if "EmailStr" in normalized:
        normalized = _replace_email_str(normalized)
        report.repairs.append("Replaced EmailStr with str to avoid optional email-validator dependency.")

    report.code = normalized
    report.issues.extend(find_backend_code_issues(normalized))
    return report


def find_backend_code_issues(code: str) -> list[str]:
    issues: list[str] = []

    if "EmailStr" in code:
        issues.append("Uses EmailStr, which requires optional email-validator dependency.")

    if re.search(r"constr\(\s*regex\s*=", code):
        issues.append("Uses Pydantic v1 constr(regex=...) instead of constr(pattern=...).")

    if re.search(r"response_model\s*=\s*dict\b", code):
        issues.append("Uses response_model=dict instead of an explicit Pydantic response model.")

    if re.search(r"response_model\s*=\s*Dict\s*\[", code):
        issues.append("Uses response_model=Dict[...] where an explicit response model is safer.")

    missing_response_model = _routes_missing_response_model(code)
    if missing_response_model:
        joined = ", ".join(missing_response_model)
        issues.append(f"Routes missing explicit response_model: {joined}")

    return issues


def _replace_email_str(code: str) -> str:
    normalized = re.sub(r",\s*EmailStr", "", code)
    normalized = re.sub(r"EmailStr\s*,\s*", "", normalized)
    return re.sub(r"\bEmailStr\b", "str", normalized)


def _routes_missing_response_model(code: str) -> list[str]:
    missing: list[str] = []
    pattern = re.compile(r"@app\.(get|post|put|patch|delete)\((?P<args>.*?)\)", re.DOTALL)
    for match in pattern.finditer(code):
        args = match.group("args")
        if "response_model" not in args:
            path_match = re.search(r"['\"]([^'\"]+)['\"]", args)
            path = path_match.group(1) if path_match else "<unknown>"
            missing.append(f"{match.group(1).upper()} {path}")
    return missing
