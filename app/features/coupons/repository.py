from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.coupons.models import Coupon


class CouponRepository(BaseRepository[Coupon]):
    model = Coupon

    async def get_by_code(self, code: str) -> Coupon | None:
        result = await self.session.execute(select(Coupon).where(Coupon.code == code))
        return result.scalar_one_or_none()
