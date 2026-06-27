from fastapi.testclient import TestClient
from sandbox_app import app

client = TestClient(app)

def test_add_item():
    response = client.post("/items", json={"name": "Widget", "sku": "WDG-001", "quantity": 100})
    assert response.status_code == 201
    assert response.json()["message"] == "Item added successfully"
    assert response.json()["item"]["name"] == "Widget"
    assert response.json()["item"]["sku"] == "WDG-001"
    assert response.json()["item"]["quantity"] == 100

def test_add_duplicate_sku():
    response = client.post("/items", json={"name": "Widget", "sku": "WDG-001", "quantity": 100})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_add_item_negative_quantity():
    response = client.post("/items", json={"name": "Gadget", "sku": "GDT-002", "quantity": -10})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_list_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_list_items_with_data():
    client.post("/items", json={"name": "Widget", "sku": "WDG-001", "quantity": 100})
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "WDG-001"

def test_retrieve_item_by_sku():
    response = client.get("/items/WDG-001")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"
    assert response.json()["sku"] == "WDG-001"
    assert response.json()["quantity"] == 100

def test_retrieve_non_existent_item():
    response = client.get("/items/INVALID-SKU")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_sell_item_success():
    response = client.post("/items/WDG-001/sell", json={"amount": 30})
    assert response.status_code == 200
    assert response.json()["message"] == "Stock decremented successfully"
    assert response.json()["item"]["quantity"] == 70

def test_sell_item_insufficient_stock():
    response = client.post("/items/WDG-001/sell", json={"amount": 100})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_sell_non_existent_item():
    response = client.post("/items/INVALID-SKU/sell", json={"amount": 1})
    assert response.status_code == 404
    assert "detail" in response.json()