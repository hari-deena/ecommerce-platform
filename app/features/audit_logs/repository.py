from app.common.repository import BaseRepository
from app.features.audit_logs.models import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog
