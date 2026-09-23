"""seed default roles (admin/user/guest) and the default admin account

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-23

"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.security import hash_password

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Keep in sync with app.common.enums.RoleName / RoleId — the ids are
# explicit (not left to autoincrement) so they're stable, human-referenceable
# constants across every environment this migration runs in.
DEFAULT_ROLES = [(1, "admin"), (2, "user"), (3, "guest")]

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PHONE = "6379400448"
ADMIN_PASSWORD = "Admin@123"  # noqa: S105 — seed-only default; rotate after first login.
ADMIN_FULL_NAME = "Admin"

roles_table = sa.table(
    "roles",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String()),
)
users_table = sa.table(
    "users",
    sa.column("id", sa.UUID()),
    sa.column("email", sa.String()),
    sa.column("password_hash", sa.String()),
    sa.column("is_active", sa.Boolean()),
    sa.column("role_id", sa.Integer()),
)
customers_table = sa.table(
    "customers",
    sa.column("id", sa.UUID()),
    sa.column("user_id", sa.UUID()),
    sa.column("full_name", sa.String()),
    sa.column("phone", sa.String()),
)


def upgrade() -> None:
    conn = op.get_bind()

    for role_id, name in DEFAULT_ROLES:
        exists = conn.execute(
            sa.select(roles_table.c.id).where(roles_table.c.id == role_id)
        ).first()
        if exists is None:
            conn.execute(roles_table.insert().values(id=role_id, name=name))

    admin_role_id = DEFAULT_ROLES[0][0]  # 1
    existing_admin = conn.execute(
        sa.select(users_table.c.id).where(users_table.c.email == ADMIN_EMAIL)
    ).first()
    if existing_admin is None:
        admin_user_id = uuid.uuid4()
        conn.execute(
            users_table.insert().values(
                id=admin_user_id,
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                is_active=True,
                role_id=admin_role_id,
            )
        )
        conn.execute(
            customers_table.insert().values(
                id=uuid.uuid4(),
                user_id=admin_user_id,
                full_name=ADMIN_FULL_NAME,
                phone=ADMIN_PHONE,
            )
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM customers WHERE user_id IN (SELECT id FROM users WHERE email = :email)"
        ),
        {"email": ADMIN_EMAIL},
    )
    conn.execute(users_table.delete().where(users_table.c.email == ADMIN_EMAIL))
    conn.execute(
        roles_table.delete().where(roles_table.c.id.in_([r[0] for r in DEFAULT_ROLES]))
    )
