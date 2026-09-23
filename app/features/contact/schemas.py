from pydantic import BaseModel, EmailStr

from app.common.schemas import IDTimestampSchema
from app.features.contact.models import ContactStatus


class ContactEnquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    subject: str
    message: str


class ContactStatusUpdate(BaseModel):
    status: ContactStatus


class ContactEnquiryRead(IDTimestampSchema):
    name: str
    email: EmailStr
    phone: str | None
    subject: str
    message: str
    status: ContactStatus
