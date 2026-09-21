from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud_router import build_crud_router
from app.db.session import get_db
from app.features.categories.repository import CategoryRepository
from app.features.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.features.categories.service import CategoryService


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(db))


# PG-002/PG-003 (public browsing) read publicly; PG-A004 (Category Management) admin-only writes.
router = build_crud_router(
    service_dependency=get_category_service,
    create_schema=CategoryCreate,
    update_schema=CategoryUpdate,
    read_schema=CategoryRead,
    prefix="/categories",
    tags=["categories"],
    require_admin_read=False,
    require_admin_write=True,
)
