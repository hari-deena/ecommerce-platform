import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user
from app.db.session import get_db
from app.features.cart.repository import CartItemRepository, CartRepository
from app.features.cart.schemas import (
    AddCartItemRequest,
    ApplyCouponRequest,
    CartRead,
    UpdateCartItemRequest,
)
from app.features.cart.service import CartService
from app.features.coupons.repository import CouponRepository
from app.features.coupons.service import CouponService
from app.features.products.repository import ProductRepository
from app.features.users.models import User

router = APIRouter(prefix="/cart", tags=["cart"], dependencies=[Depends(get_current_active_user)])


def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(
        CartRepository(db),
        CartItemRepository(db),
        ProductRepository(db),
        CouponService(CouponRepository(db)),
    )


@router.get("/", response_model=CartRead)
async def get_my_cart(
    user: User = Depends(get_current_active_user), service: CartService = Depends(get_cart_service)
) -> dict:
    return await service.get_view(user.id)


@router.post("/items", response_model=CartRead)
async def add_item(
    payload: AddCartItemRequest,
    user: User = Depends(get_current_active_user),
    service: CartService = Depends(get_cart_service),
) -> dict:
    return await service.add_item(user.id, payload)


@router.patch("/items/{product_id}", response_model=CartRead)
async def update_item(
    product_id: uuid.UUID,
    payload: UpdateCartItemRequest,
    user: User = Depends(get_current_active_user),
    service: CartService = Depends(get_cart_service),
) -> dict:
    return await service.update_item_quantity(user.id, product_id, payload.quantity)


@router.delete("/items/{product_id}", response_model=CartRead)
async def remove_item(
    product_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: CartService = Depends(get_cart_service),
) -> dict:
    return await service.remove_item(user.id, product_id)


@router.post("/apply-coupon", response_model=CartRead)
async def apply_coupon(
    payload: ApplyCouponRequest,
    user: User = Depends(get_current_active_user),
    service: CartService = Depends(get_cart_service),
) -> dict:
    return await service.apply_coupon(user.id, payload.code)


@router.delete("/coupon", response_model=CartRead)
async def remove_coupon(
    user: User = Depends(get_current_active_user), service: CartService = Depends(get_cart_service)
) -> dict:
    return await service.remove_coupon(user.id)
