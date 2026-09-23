from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user
from app.common.crud_router import build_crud_router
from app.db.session import get_db
from app.features.feedback.models import Feedback
from app.features.feedback.repository import FeedbackRepository
from app.features.feedback.schemas import FeedbackCreate, FeedbackRead, FeedbackStatusUpdate
from app.features.feedback.service import FeedbackService
from app.features.users.models import User


def get_feedback_service(db: AsyncSession = Depends(get_db)) -> FeedbackService:
    return FeedbackService(FeedbackRepository(db))


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    user: User = Depends(get_current_active_user),
    service: FeedbackService = Depends(get_feedback_service),
) -> Feedback:
    return await service.create_for_user(user.id, payload)


# PG-A008 — admin list/review/archive.
admin_router = build_crud_router(
    service_dependency=get_feedback_service,
    create_schema=FeedbackCreate,
    update_schema=FeedbackStatusUpdate,
    read_schema=FeedbackRead,
    prefix="/admin/feedback",
    tags=["admin:feedback"],
    require_admin_read=True,
    require_admin_write=True,
)
# NOTE: exported separately, not nested under `router` — see users/router.py note.
