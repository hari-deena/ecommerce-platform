from enum import StrEnum


class RoleName(StrEnum):
    """Canonical role names. Also the exact `roles.name` values seeded by
    `0003_seed_roles_and_admin` — keep in sync. `RoleId` below mirrors the
    seeded integer ids for code that needs to reference a role without a
    DB round-trip (e.g. the admin seed migration itself)."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class RoleId:
    """Seeded `roles.id` values — matches `RoleName` 1:1. Not an IntEnum
    because these are DB-assigned surrogate keys, not a fixed language-level
    enumeration; keep this in sync with `0003_seed_roles_and_admin`."""

    ADMIN = 1
    USER = 2
    GUEST = 3
