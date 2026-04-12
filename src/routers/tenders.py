from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.infra.settings.database import get_session
from src.schemas import (
    FilterTenderSchema,
    MessageSchema,
    TenderCreateSchema,
    TenderListSchema,
    TenderPublicSchema,
    TenderUpdateSchema,
)
from src.security import get_current_user
from src.services.company_service import CompanyService
from src.services.tender_service import TenderService

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]

router = APIRouter(prefix="/companies/{company_id}/tenders", tags=["tenders"])


@router.post("/", response_model=TenderPublicSchema)
async def create_tender(
    company_id: int,
    tender: TenderCreateSchema,
    user: CurrentUser,
    session: Session,
):
    await CompanyService(session).get_owned(company_id, user.id)
    return await TenderService(session).create(company_id, tender)


@router.get("/", response_model=TenderListSchema)
async def list_tenders(
    company_id: int,
    session: Session,
    user: CurrentUser,
    tender_filter: Annotated[FilterTenderSchema, Query()],
):
    await CompanyService(session).get_owned(company_id, user.id)
    tenders = await TenderService(session).list(company_id, tender_filter)
    return {"tenders": tenders}


@router.patch("/{tender_id}", response_model=TenderPublicSchema)
async def patch_tender(
    company_id: int,
    tender_id: int,
    tender: TenderUpdateSchema,
    user: CurrentUser,
    session: Session,
):
    await CompanyService(session).get_owned(company_id, user.id)
    return await TenderService(session).update(tender_id, company_id, tender)


@router.delete("/{tender_id}", response_model=MessageSchema)
async def delete_tender(
    company_id: int,
    tender_id: int,
    user: CurrentUser,
    session: Session,
):
    await CompanyService(session).get_owned(company_id, user.id)
    await TenderService(session).delete(tender_id, company_id)
    return {"message": "Tender has been deleted successfully."}
