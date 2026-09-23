import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema


class ProductCreate(BaseModel):
    name: str
    slug: str
    category_id: uuid.UUID
    description: str | None = None
    ingredients: str | None = None
    suitable_for: str | None = None
    price: Decimal
    discount_price: Decimal | None = None
    stock_quantity: int = 0
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    category_id: uuid.UUID | None = None
    description: str | None = None
    ingredients: str | None = None
    suitable_for: str | None = None
    price: Decimal | None = None
    discount_price: Decimal | None = None
    is_active: bool | None = None
    # stock_quantity intentionally excluded — mutate stock only via the
    # `inventory` feature so every change is captured in the audit ledger.


class ProductRead(IDTimestampSchema):
    name: str
    slug: str
    category_id: uuid.UUID
    description: str | None
    ingredients: str | None
    suitable_for: str | None
    price: Decimal
    discount_price: Decimal | None
    stock_quantity: int
    is_active: bool

    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0
