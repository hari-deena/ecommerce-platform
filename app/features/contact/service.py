from app.common.service import BaseService
from app.features.contact.models import ContactEnquiry
from app.features.contact.repository import ContactRepository
from app.features.contact.schemas import ContactEnquiryCreate, ContactStatusUpdate


class ContactService(BaseService[ContactEnquiry, ContactEnquiryCreate, ContactStatusUpdate]):
    not_found_message = "Contact enquiry not found"

    def __init__(self, repository: ContactRepository) -> None:
        super().__init__(repository)
        self.repository: ContactRepository = repository

    # TODO: notify the sales/support inbox by email when a new enquiry comes in.
