from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr, conint
from typing import List, Dict

app = FastAPI()
store: Dict[str, dict] = {}

class ItemCreate(BaseModel):
    name: str = Field(..., max_length=255)
    sku: constr(strict=True, min_length=1)
    quantity: conint(ge=0)

class ItemResponse(BaseModel):
    name: str
    sku: str
    quantity: int

class SellItemRequest(BaseModel):
    amount: conint(ge=1)

@app.post("/items", response_model=Dict[str, ItemResponse], status_code=201)
def add_item(item: ItemCreate):
    if item.sku in store:
        raise HTTPException(status_code=400, detail="SKU must be unique")
    store[item.sku] = {"name": item.name, "sku": item.sku, "quantity": item.quantity}
    return {"message": "Item added successfully", "item": ItemResponse(**store[item.sku])}

@app.get("/items", response_model=List[ItemResponse])
def list_items():
    return [ItemResponse(**item) for item in store.values()]

@app.get("/items/{sku}", response_model=ItemResponse)
def get_item(sku: str):
    item = store.get(sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(**item)

@app.post("/items/{sku}/sell", response_model=Dict[str, ItemResponse])
def sell_item(sku: str, sell_request: SellItemRequest):
    item = store.get(sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["quantity"] < sell_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    item["quantity"] -= sell_request.amount
    return {"message": "Item sold successfully", "item": ItemResponse(**item)}