from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, conint, validator
from typing import List, Dict

app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    sku: constr(min_length=1)
    quantity: conint(ge=0)

class ItemResponse(BaseModel):
    name: str
    sku: str
    quantity: int

class SellItemRequest(BaseModel):
    amount: conint(ge=1)

# In-memory storage for items
items: Dict[str, ItemResponse] = {}

@app.post("/items", response_model=dict, status_code=201)
def add_item(item: ItemCreate):
    if item.sku in items:
        raise HTTPException(status_code=400, detail="SKU must be unique")
    new_item = ItemResponse(name=item.name, sku=item.sku, quantity=item.quantity)
    items[item.sku] = new_item
    return {"message": "Item added successfully", "item": new_item}

@app.get("/items", response_model=List[ItemResponse])
def list_items():
    return list(items.values())

@app.get("/items/{sku}", response_model=ItemResponse)
def get_item(sku: str):
    if sku not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[sku]

@app.post("/items/{sku}/sell", response_model=dict)
def sell_item(sku: str, sell_request: SellItemRequest):
    if sku not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = items[sku]
    if item.quantity < sell_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    item.quantity -= sell_request.amount
    return {"message": "Stock decremented successfully", "item": item}