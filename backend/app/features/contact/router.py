from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud_router import build_crud_router
from app.db.session import get_db
from app.features.contact.models import ContactEnquiry
from app.features.contact.repository import ContactRepository
from app.features.contact.schemas import (
    ContactEnquiryCreate,
    ContactEnquiryRead,
    ContactStatusUpdate,
)
from app.features.contact.service import ContactService


def get_contact_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    return ContactService(ContactRepository(db))


router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/", response_model=ContactEnquiryRead, status_code=status.HTTP_201_CREATED)
async def submit_enquiry(
    payload: ContactEnquiryCreate, service: ContactService = Depends(get_contact_service)
) -> ContactEnquiry:
    """Public — no authentication required (PG-006)."""
    return await service.create(payload)


# PG-A009 — admin list/manage.
admin_router = build_crud_router(
    service_dependency=get_contact_service,
    create_schema=ContactEnquiryCreate,
    update_schema=ContactStatusUpdate,
    read_schema=ContactEnquiryRead,
    prefix="/admin/contact",
    tags=["admin:contact"],
    require_admin_read=True,
    require_admin_write=True,
)
# NOTE: exported separately, not nested under `router` — see users/router.py note.
