from fastapi import FastAPI

from app.deploy.loader import extract_openapi, load_fastapi_app, registry


def test_load_fastapi_app_and_openapi():
    code = (
        "from fastapi import FastAPI\n"
        "app = FastAPI(title='Test')\n"
        "@app.get('/ping')\n"
        "def ping(): return {'pong': True}\n"
    )
    app_instance = load_fastapi_app(code, module_name="test_load_app")
    assert isinstance(app_instance, FastAPI)
    schema = extract_openapi(app_instance)
    assert "/ping" in schema["paths"]


def test_registry_stores_deployment():
    from app.deploy.loader import Deployment
    from pathlib import Path

    dep = Deployment(
        deployment_id="abc123",
        feature_request="test",
        blueprint="blueprint",
        backend_code="code",
        test_code="tests",
        frontend_html="<html></html>",
        openapi_schema={},
        api_mount_path="/live/abc123",
        ui_path="/ui/abc123",
        workspace=Path("generated/abc123"),
    )
    registry.register(dep)
    assert registry.get("abc123") is not None
