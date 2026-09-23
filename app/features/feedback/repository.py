from app.common.repository import BaseRepository
from app.features.feedback.models import Feedback


class FeedbackRepository(BaseRepository[Feedback]):
    model = Feedback
