import uuid

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema


class InventoryAdjustmentCreate(BaseModel):
    product_id: uuid.UUID
    change_quantity: int  # positive = restock, negative = manual deduction/write-off
    reason: str


class InventoryAdjustmentRead(IDTimestampSchema):
    product_id: uuid.UUID
    change_quantity: int
    previous_stock: int
    new_stock: int
    reason: str
    created_by: uuid.UUID | None
