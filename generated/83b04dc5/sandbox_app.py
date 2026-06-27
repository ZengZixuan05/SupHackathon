from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, conint
from typing import List, Dict

app = FastAPI()
store: Dict[str, dict] = {}

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

@app.post("/items", response_model=dict, status_code=201)
async def add_item(item: ItemCreate):
    if item.sku in store:
        raise HTTPException(status_code=409, detail="SKU already exists")
    
    store[item.sku] = {"name": item.name, "sku": item.sku, "quantity": item.quantity}
    return {"message": "Item added successfully", "item": store[item.sku]}

@app.get("/items", response_model=List[ItemResponse])
async def list_items():
    return [ItemResponse(**item) for item in store.values()]

@app.get("/items/{sku}", response_model=ItemResponse)
async def get_item(sku: str):
    item = store.get(sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(**item)

@app.post("/items/{sku}/sell", response_model=dict)
async def sell_item(sku: str, sell_request: SellItemRequest):
    item = store.get(sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item["quantity"] < sell_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    item["quantity"] -= sell_request.amount
    return {"message": "Stock decremented successfully", "item": ItemResponse(**item)}