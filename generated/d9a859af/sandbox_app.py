from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, conint, field_validator
from typing import List, Dict

app = FastAPI()
store: Dict[str, Dict] = {}

class ItemCreate(BaseModel):
    name: str
    sku: constr(min_length=1)  # SKU must be a non-empty string
    quantity: conint(ge=0)      # Quantity must be ≥ 0

    @field_validator('sku')
    def sku_must_be_unique(cls, sku):
        if sku in store:
            raise ValueError("SKU must be unique")
        return sku

class ItemResponse(BaseModel):
    name: str
    sku: str
    quantity: conint(ge=0)

class SellItemRequest(BaseModel):
    amount: conint(ge=1)  # Amount must be ≥ 1

@app.post("/items", response_model=Dict[str, ItemResponse], status_code=201)
def add_item(item: ItemCreate):
    store[item.sku] = {"name": item.name, "sku": item.sku, "quantity": item.quantity}
    return {"message": "Item added successfully", "item": ItemResponse(**store[item.sku])}

@app.get("/items", response_model=List[ItemResponse])
def list_items():
    return [ItemResponse(**item) for item in store.values()]

@app.get("/items/{sku}", response_model=ItemResponse)
def get_item(sku: str):
    item = store.get(sku)
    if item is None:
        raise HTTPException(status_code=404, detail={"error": "Item not found"})
    return ItemResponse(**item)

@app.post("/items/{sku}/sell", response_model=Dict[str, ItemResponse])
def sell_item(sku: str, sell_request: SellItemRequest):
    item = store.get(sku)
    if item is None:
        raise HTTPException(status_code=404, detail={"error": "Item not found"})
    if item["quantity"] < sell_request.amount:
        raise HTTPException(status_code=400, detail={"error": "Insufficient stock"})
    
    item["quantity"] -= sell_request.amount
    return {"message": "Stock decremented successfully", "item": ItemResponse(**item)}