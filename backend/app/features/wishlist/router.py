import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user
from app.db.session import get_db
from app.features.cart.repository import CartItemRepository, CartRepository
from app.features.cart.schemas import CartRead
from app.features.cart.service import CartService
from app.features.coupons.repository import CouponRepository
from app.features.coupons.service import CouponService
from app.features.products.repository import ProductRepository
from app.features.users.models import User
from app.features.wishlist.models import WishlistItem
from app.features.wishlist.repository import WishlistRepository
from app.features.wishlist.schemas import WishlistItemCreate, WishlistItemRead
from app.features.wishlist.service import WishlistService

router = APIRouter(
    prefix="/wishlist", tags=["wishlist"], dependencies=[Depends(get_current_active_user)]
)


def get_wishlist_service(db: AsyncSession = Depends(get_db)) -> WishlistService:
    return WishlistService(WishlistRepository(db))


def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(
        CartRepository(db),
        CartItemRepository(db),
        ProductRepository(db),
        CouponService(CouponRepository(db)),
    )


@router.get("/", response_model=list[WishlistItemRead])
async def list_my_wishlist(
    user: User = Depends(get_current_active_user),
    service: WishlistService = Depends(get_wishlist_service),
) -> list[WishlistItem]:
    return await service.list_for_user(user.id)


@router.post("/", response_model=WishlistItemRead, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    payload: WishlistItemCreate,
    user: User = Depends(get_current_active_user),
    service: WishlistService = Depends(get_wishlist_service),
) -> WishlistItem:
    return await service.add(user.id, payload.product_id)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: WishlistService = Depends(get_wishlist_service),
) -> None:
    await service.remove(user.id, product_id)


@router.post("/{product_id}/move-to-cart", response_model=CartRead)
async def move_to_cart(
    product_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: WishlistService = Depends(get_wishlist_service),
    cart_service: CartService = Depends(get_cart_service),
) -> dict:
    return await service.move_to_cart(user.id, product_id, cart_service)
