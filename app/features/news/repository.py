from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.news.models import NewsArticle


class NewsRepository(BaseRepository[NewsArticle]):
    model = NewsArticle

    async def list_published(self, *, skip: int = 0, limit: int = 50) -> list[NewsArticle]:
        result = await self.session.execute(
            select(NewsArticle)
            .where(NewsArticle.is_published.is_(True))
            .order_by(NewsArticle.published_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
