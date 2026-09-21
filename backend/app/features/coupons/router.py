from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud_router import build_crud_router
from app.db.session import get_db
from app.features.coupons.repository import CouponRepository
from app.features.coupons.schemas import CouponCreate, CouponRead, CouponUpdate
from app.features.coupons.service import CouponService


def get_coupon_service(db: AsyncSession = Depends(get_db)) -> CouponService:
    return CouponService(CouponRepository(db))


# PG-A006 — admin-only management. Customers never browse this list; they apply
# a code via `cart`/`orders`, which call CouponService.validate_and_price directly.
router = build_crud_router(
    service_dependency=get_coupon_service,
    create_schema=CouponCreate,
    update_schema=CouponUpdate,
    read_schema=CouponRead,
    prefix="/admin/coupons",
    tags=["admin:coupons"],
    require_admin_read=True,
    require_admin_write=True,
)
