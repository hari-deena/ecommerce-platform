from app.common.service import BaseService
from app.features.news.models import NewsArticle
from app.features.news.repository import NewsRepository
from app.features.news.schemas import NewsArticleCreate, NewsArticleUpdate


class NewsService(BaseService[NewsArticle, NewsArticleCreate, NewsArticleUpdate]):
    not_found_message = "News article not found"

    def __init__(self, repository: NewsRepository) -> None:
        super().__init__(repository)
        self.repository: NewsRepository = repository

    async def list_published(self, *, skip: int = 0, limit: int = 50) -> list[NewsArticle]:
        return await self.repository.list_published(skip=skip, limit=limit)
