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

def test_add_item():
    response = client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    assert response.status_code == 201
    assert response.json()["message"] == "Item added successfully"
    item = response.json()["item"]
    assert item["name"] == "Widget"
    assert item["sku"] == "TEST-001"
    assert item["quantity"] == 100

def test_add_duplicate_sku():
    client.post("/items", json={"name": "Widget", "sku": "TEST-001", "quantity": 100})
    response = client.post("/items", json={"name": "Gadget", "sku": "TEST-001", "quantity": 50})
    assert response.status_code == 409
    assert "detail" in response.json()

def test_add_item_with_negative_quantity():
    response = client.post("/items", json={"name": "Widget", "sku": "TEST-002", "quantity": -10})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_list_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_list_items_with_multiple_items():
    client.post("/items", json={"name": "Widget", "sku": "TEST-003", "quantity": 100})
    client.post("/items", json={"name": "Gadget", "sku": "TEST-004", "quantity": 50})
    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2

def test_get_item_by_sku():
    client.post("/items", json={"name": "Widget", "sku": "TEST-005", "quantity": 100})
    response = client.get("/items/TEST-005")
    assert response.status_code == 200
    item = response.json()
    assert item["name"] == "Widget"
    assert item["sku"] == "TEST-005"
    assert item["quantity"] == 100

def test_get_non_existing_item():
    response = client.get("/items/TEST-999")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_sell_item_with_sufficient_stock():
    client.post("/items", json={"name": "Widget", "sku": "TEST-006", "quantity": 100})
    response = client.post("/items/TEST-006/sell", json={"amount": 30})
    assert response.status_code == 200
    assert response.json()["message"] == "Stock decremented successfully"
    item = response.json()["item"]
    assert item["quantity"] == 70

def test_sell_item_with_insufficient_stock():
    client.post("/items", json={"name": "Widget", "sku": "TEST-007", "quantity": 20})
    response = client.post("/items/TEST-007/sell", json={"amount": 30})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_sell_non_existing_item():
    response = client.post("/items/TEST-999/sell", json={"amount": 1})
    assert response.status_code == 404
    assert "detail" in response.json()