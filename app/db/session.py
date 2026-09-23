from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
