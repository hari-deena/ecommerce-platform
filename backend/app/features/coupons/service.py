from datetime import UTC, datetime
from decimal import Decimal

from app.common.service import BaseService
from app.core.exceptions import ValidationAppError
from app.features.coupons.models import Coupon, DiscountType
from app.features.coupons.repository import CouponRepository
from app.features.coupons.schemas import CouponCreate, CouponUpdate


class CouponService(BaseService[Coupon, CouponCreate, CouponUpdate]):
    not_found_message = "Coupon not found"

    def __init__(self, repository: CouponRepository) -> None:
        super().__init__(repository)
        self.repository: CouponRepository = repository

    async def validate_and_price(self, code: str, subtotal: Decimal) -> tuple[Coupon, Decimal]:
        """Used by `cart`/`orders` when a customer applies a coupon at checkout.

        Returns the coupon and the computed discount amount, or raises
        ValidationAppError with a customer-facing reason.
        """
        coupon = await self.repository.get_by_code(code.upper())
        if coupon is None or not coupon.is_active:
            raise ValidationAppError("Invalid coupon code")

        now = datetime.now(UTC)
        if not (coupon.start_date <= now <= coupon.expiry_date):
            raise ValidationAppError("This coupon is not currently active")

        if coupon.usage_limit is not None and coupon.times_used >= coupon.usage_limit:
            raise ValidationAppError("This coupon has reached its usage limit")

        if coupon.min_purchase_amount is not None and subtotal < coupon.min_purchase_amount:
            raise ValidationAppError(
                f"A minimum purchase of {coupon.min_purchase_amount} is required for this coupon"
            )

        if coupon.discount_type == DiscountType.PERCENTAGE:
            discount = subtotal * (coupon.discount_value / Decimal(100))
        else:
            discount = coupon.discount_value

        if coupon.max_discount_amount is not None:
            discount = min(discount, coupon.max_discount_amount)

        return coupon, min(discount, subtotal)

    async def record_usage(self, coupon: Coupon) -> None:
        await self.repository.update(coupon, {"times_used": coupon.times_used + 1})
