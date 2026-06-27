import pytest
from fastapi.testclient import TestClient
from sandbox_app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
    import sandbox_app
    if hasattr(sandbox_app, "store"):
        sandbox_app.store.clear()
    yield
    if hasattr(sandbox_app, "store"):
        sandbox_app.store.clear()

def test_add_item_success():
    response = client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    assert response.status_code == 201
    assert "message" in response.json()
    assert "item" in response.json()
    item = response.json()["item"]
    assert item["name"] == "Widget"
    assert item["sku"] == "TEST-001"
    assert item["quantity"] == 100

def test_add_item_duplicate_sku():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    response = client.post("/items", json={"name": "Gadget", "sku": "TEST-001", "quantity": 50})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_list_items():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    client.post("/items", json={"name": "Gadget", "sku": "TEST-002", "quantity": 50})
    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2

def test_get_item_success():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    response = client.get("/items/TEST-001")
    assert response.status_code == 200
    item = response.json()
    assert item["name"] == "Widget"
    assert item["sku"] == "TEST-001"
    assert item["quantity"] == 100

def test_get_item_not_found():
    response = client.get("/items/INVALID-SKU")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_sell_item_success():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    response = client.post("/items/TEST-001/sell", json={"amount": 30})
    assert response.status_code == 200
    item = response.json()["item"]
    assert item["quantity"] == 70

def test_sell_item_insufficient_stock():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 10})
    response = client.post("/items/TEST-001/sell", json={"amount": 20})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_sell_item_not_found():
    response = client.post("/items/INVALID-SKU/sell", json={"amount": 1})
    assert response.status_code == 404
    assert "detail" in response.json()

def test_add_item_negative_quantity():
    response = client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": -1})
    assert response.status_code == 422

def test_sell_item_negative_amount():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    response = client.post("/items/TEST-001/sell", json={"amount": -5})
    assert response.status_code == 422