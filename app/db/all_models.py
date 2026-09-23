"""Import every feature's models so `Base.metadata` is fully populated.

Used by Alembic (`alembic/env.py`) for autogenerate and by the test suite
(`tests/conftest.py`) for `Base.metadata.create_all`. Nothing in `app/` should
import this module for any other reason — routers/services import the
specific feature model they need directly.

Scoped down to only `users`/`customers`/`roles` for now, matching the current
migration set (0002-0004) — the other features' tables don't have migrations
yet. Restore the rest of these imports (see git history) when a feature's
migration is actually being generated.
"""

from app.features.users.models import Customer, Role, User  # noqa: F401
