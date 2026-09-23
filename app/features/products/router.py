from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud_router import build_crud_router
from app.db.session import get_db
from app.features.products.repository import ProductRepository
from app.features.products.schemas import ProductCreate, ProductRead, ProductUpdate
from app.features.products.service import ProductService


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))


# PG-002/PG-003 read publicly; PG-A003 (Product Management) admin-only writes.
router = build_crud_router(
    service_dependency=get_product_service,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    read_schema=ProductRead,
    prefix="/products",
    tags=["products"],
    require_admin_read=False,
    require_admin_write=True,
)

# TODO: GET /products/search?q=&category=&min_price=&max_price= once filter UX is confirmed.
