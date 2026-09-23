import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Role(Base):
    """Small, mostly-static lookup table — deliberately a plain integer PK
    (not UUID like everything else) so the seeded ids are stable,
    human-referenceable constants: 1=admin, 2=user, 3=guest. See
    `app.common.enums.RoleName` for the canonical names and
    `0003_seed_roles_and_admin` for the seed data."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Auth identity only — owned by the `users` feature, used by `auth` for
    login/registration. Profile fields (name/phone) live on `Customer`."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Indexed: admin listings and access checks commonly filter WHERE is_active
    # = true; without this it's a full table scan once the table has any real
    # volume of users.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)

    role: Mapped["Role"] = relationship()
    customer: Mapped["Customer | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def has_role(self, name: str) -> bool:
        return self.role is not None and self.role.name == name


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer-facing profile, split out from `User` (auth identity)."""

    __tablename__ = "customers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    # Indexed: admin customer listing sorts/searches by name (ORDER BY,
    # prefix ILIKE) — without it that's a full table scan + sort at scale.
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    user: Mapped["User"] = relationship(back_populates="customer")


class Address(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "addresses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String(50), default="home")
    line1: Mapped[str] = mapped_column(String(255))
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(100), default="India")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="addresses")
