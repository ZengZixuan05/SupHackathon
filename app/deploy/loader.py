import importlib.util
import logging
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class Deployment:
    deployment_id: str
    feature_request: str
    blueprint: str
    backend_code: str
    test_code: str
    frontend_html: str
    openapi_schema: dict[str, Any]
    api_mount_path: str
    ui_path: str
    workspace: Path


class DeploymentRegistry:
    """In-memory registry of production-ready generated features."""

    def __init__(self) -> None:
        self._deployments: dict[str, Deployment] = {}

    def get(self, deployment_id: str) -> Deployment | None:
        return self._deployments.get(deployment_id)

    def list_all(self) -> list[Deployment]:
        return list(self._deployments.values())

    def register(self, deployment: Deployment) -> None:
        self._deployments[deployment.deployment_id] = deployment


registry = DeploymentRegistry()


def create_run_id() -> str:
    return uuid.uuid4().hex[:8]


def save_artifacts(
    run_id: str,
    backend_code: str,
    test_code: str,
    frontend_html: str = "",
) -> Path:
    workspace = settings.generated_dir / run_id
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "sandbox_app.py.txt").write_text(backend_code, encoding="utf-8")
    (workspace / "test_sandbox.py.txt").write_text(test_code, encoding="utf-8")
    if frontend_html:
        (workspace / "ui.html").write_text(frontend_html, encoding="utf-8")
    return workspace


def load_fastapi_app(code: str, module_name: str = "generated_sandbox") -> FastAPI:
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    if spec is None:
        raise RuntimeError("Failed to create module spec")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    exec(compile(code, f"{module_name}.py", "exec"), module.__dict__)  # noqa: S102

    app_instance = getattr(module, "app", None)
    if app_instance is None or not isinstance(app_instance, FastAPI):
        raise RuntimeError("Generated code must define a FastAPI instance named `app`")
    return app_instance


def extract_openapi(app_instance: FastAPI) -> dict[str, Any]:
    return app_instance.openapi()


def mount_generated_app(host_app: FastAPI, deployment_id: str, backend_code: str) -> str:
    """Dynamically mount a generated FastAPI sub-app. Returns the mount path."""
    module_name = f"generated_{deployment_id}"
    sub_app = load_fastapi_app(backend_code, module_name=module_name)
    mount_path = f"/live/{deployment_id}"
    host_app.mount(mount_path, sub_app)
    logger.info("Mounted generated API at %s", mount_path)
    return mount_path
