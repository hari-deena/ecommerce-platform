import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.config import settings
from app.db import all_models  # noqa: F401 — populates Base.metadata via feature imports
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Tables whose model is defined (so Base.metadata always includes it — e.g.
# `Address` lives in the same module as `User`/`Customer`/`Role`) but that
# don't have a migration yet. Autogenerate/`alembic check` would otherwise
# permanently flag these as pending drift. Remove a name here once its own
# migration is created.
NOT_YET_MIGRATED = {"addresses"}


def include_object(object, name, type_, reflected, compare_to) -> bool:
    return not (type_ == "table" and name in NOT_YET_MIGRATED)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.SQLALCHEMY_DATABASE_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata, include_object=include_object
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
