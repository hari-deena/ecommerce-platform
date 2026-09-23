from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Explicit naming convention so Alembic autogenerate produces stable, predictable
# constraint names instead of DB-driver-generated ones (critical for reliable diffs).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Every feature's SQLAlchemy models inherit from this. Deliberately has no
    knowledge of any feature module — see `app.db.all_models` for the registry
    that imports every model for Alembic autogenerate / `create_all` in tests.
    Importing feature models here would create a circular import, since those
    models import `Base` from this module.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
