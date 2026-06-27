# Inventory Tracking System

Build an inventory tracking system with the following capabilities:

## Requirements

- **POST /items** — Add a new inventory item with `name` (string), `sku` (string), and `quantity` (integer ≥ 0).
- **GET /items** — List all items in stock.
- **GET /items/{sku}** — Retrieve a single item by SKU.
- **POST /items/{sku}/sell** — Decrement stock by a given `amount` (integer ≥ 1). Return 400 if insufficient stock, 404 if SKU not found.

## Validation

- SKU must be unique.
- Quantity cannot go below zero.
- All responses should be JSON.

## Example Flow

1. POST `{ "name": "Widget", "sku": "WDG-001", "quantity": 100 }`
2. GET `/items/WDG-001` → `{ "name": "Widget", "sku": "WDG-001", "quantity": 100 }`
3. POST `/items/WDG-001/sell` with `{ "amount": 30 }` → quantity becomes 70
