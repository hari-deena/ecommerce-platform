import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud_router import build_crud_router
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.features.news.models import NewsArticle
from app.features.news.repository import NewsRepository
from app.features.news.schemas import NewsArticleCreate, NewsArticleRead, NewsArticleUpdate
from app.features.news.service import NewsService


def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(NewsRepository(db))


router = APIRouter(prefix="/news", tags=["news"])


@router.get("/", response_model=list[NewsArticleRead])
async def list_news(
    skip: int = 0, limit: int = 50, service: NewsService = Depends(get_news_service)
) -> list[NewsArticle]:
    return await service.list_published(skip=skip, limit=limit)


@router.get("/{article_id}", response_model=NewsArticleRead)
async def get_news_article(
    article_id: uuid.UUID, service: NewsService = Depends(get_news_service)
) -> NewsArticle:
    article = await service.get_or_404(article_id)
    if not article.is_published:
        raise NotFoundError("News article not found")
    return article


# PG-A007 — full CRUD including drafts, for admins.
admin_router = build_crud_router(
    service_dependency=get_news_service,
    create_schema=NewsArticleCreate,
    update_schema=NewsArticleUpdate,
    read_schema=NewsArticleRead,
    prefix="/admin/news",
    tags=["admin:news"],
    require_admin_read=True,
    require_admin_write=True,
)
# NOTE: exported separately, not nested under `router` — see users/router.py note.
