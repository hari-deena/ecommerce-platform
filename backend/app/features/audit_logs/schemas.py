import uuid
from typing import Any

from app.common.schemas import IDTimestampSchema


class AuditLogRead(IDTimestampSchema):
    actor_user_id: uuid.UUID | None
    action: str
    entity_type: str
    entity_id: str | None
    meta: dict[str, Any] | None
    ip_address: str | None
