from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema
from app.features.coupons.models import DiscountType


class CouponCreate(BaseModel):
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    start_date: datetime
    expiry_date: datetime
    min_purchase_amount: Decimal | None = None
    max_discount_amount: Decimal | None = None
    usage_limit: int | None = None
    is_active: bool = True


class CouponUpdate(BaseModel):
    discount_type: DiscountType | None = None
    discount_value: Decimal | None = None
    start_date: datetime | None = None
    expiry_date: datetime | None = None
    min_purchase_amount: Decimal | None = None
    max_discount_amount: Decimal | None = None
    usage_limit: int | None = None
    is_active: bool | None = None


class CouponRead(IDTimestampSchema):
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    start_date: datetime
    expiry_date: datetime
    min_purchase_amount: Decimal | None
    max_discount_amount: Decimal | None
    usage_limit: int | None
    times_used: int
    is_active: bool
