import uuid

from app.common.service import BaseService
from app.features.feedback.models import Feedback
from app.features.feedback.repository import FeedbackRepository
from app.features.feedback.schemas import FeedbackCreate, FeedbackStatusUpdate


class FeedbackService(BaseService[Feedback, FeedbackCreate, FeedbackStatusUpdate]):
    not_found_message = "Feedback not found"

    def __init__(self, repository: FeedbackRepository) -> None:
        super().__init__(repository)
        self.repository: FeedbackRepository = repository

    async def create_for_user(self, user_id: uuid.UUID, payload: FeedbackCreate) -> Feedback:
        return await self.repository.create({**payload.model_dump(), "user_id": user_id})
