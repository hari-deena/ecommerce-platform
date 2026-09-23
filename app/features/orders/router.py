import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, require_admin
from app.db.session import get_db
from app.features.cart.repository import CartItemRepository, CartRepository
from app.features.cart.service import CartService
from app.features.coupons.repository import CouponRepository
from app.features.coupons.service import CouponService
from app.features.orders.models import Order
from app.features.orders.repository import OrderItemRepository, OrderRepository
from app.features.orders.schemas import OrderRead, OrderStatusUpdate, PlaceOrderRequest
from app.features.orders.service import OrderService
from app.features.products.repository import ProductRepository
from app.features.users.models import User

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(OrderRepository(db), OrderItemRepository(db), ProductRepository(db))


def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(
        CartRepository(db),
        CartItemRepository(db),
        ProductRepository(db),
        CouponService(CouponRepository(db)),
    )


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def place_order(
    payload: PlaceOrderRequest,
    user: User = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
    cart_service: CartService = Depends(get_cart_service),
) -> Order:
    return await service.place_order(user.id, payload, cart_service)


@router.get("/", response_model=list[OrderRead])
async def list_my_orders(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
) -> list[Order]:
    return await service.list_for_user(user.id, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderRead)
async def get_my_order(
    order_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
) -> Order:
    return await service.get_owned_or_404(order_id, user.id)


@router.post("/{order_id}/reorder")
async def reorder(
    order_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
    cart_service: CartService = Depends(get_cart_service),
) -> dict:
    return await service.reorder(user.id, order_id, cart_service)


# --- Admin (PG-A010) ---

admin_router = APIRouter(
    prefix="/admin/orders", tags=["admin:orders"], dependencies=[Depends(require_admin)]
)


@admin_router.get("/", response_model=list[OrderRead])
async def list_all_orders(
    skip: int = 0, limit: int = 50, service: OrderService = Depends(get_order_service)
) -> list[Order]:
    return await service.list_all(skip=skip, limit=limit)


@admin_router.get("/{order_id}", response_model=OrderRead)
async def get_any_order(
    order_id: uuid.UUID, service: OrderService = Depends(get_order_service)
) -> Order:
    return await service.get_or_404(order_id)


@admin_router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
) -> Order:
    order = await service.get_or_404(order_id)
    return await service.update_status(order, payload.status)


# NOTE: exported separately, not nested under `router` — see users/router.py note.
