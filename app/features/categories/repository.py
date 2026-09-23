from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.categories.models import Category


class CategoryRepository(BaseRepository[Category]):
    model = Category

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()
