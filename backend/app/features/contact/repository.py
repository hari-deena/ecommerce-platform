from app.common.repository import BaseRepository
from app.features.contact.models import ContactEnquiry


class ContactRepository(BaseRepository[ContactEnquiry]):
    model = ContactEnquiry
