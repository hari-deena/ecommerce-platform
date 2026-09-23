import uuid

from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.products.models import Product


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def get_by_slug(self, slug: str) -> Product | None:
        result = await self.session.execute(select(Product).where(Product.slug == slug))
        return result.scalar_one_or_none()

    async def list_by_category(
        self, category_id: uuid.UUID, *, skip: int = 0, limit: int = 50
    ) -> list[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.category_id == category_id, Product.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    # TODO: full-text/trigram search and price-range filters once PG-002's
    # search/filter UX is finalised (PRD §15 "Product information/attributes").
