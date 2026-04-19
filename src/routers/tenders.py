from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.infra.settings.database import get_session
from src.schemas.common import MessageSchema
from src.schemas.tender import (
    FilterTenderSchema,
    TenderCreateSchema,
    TenderListSchema,
    TenderResponse,
    TenderUpdateSchema,
)
from src.security import get_current_user
from src.services.company_service import CompanyService
from src.services.tender_service import TenderService

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]


def get_tender_service(session: Session) -> TenderService:
    """Dependency provider for TenderService."""
    return TenderService(session)


def get_company_service(session: Session) -> CompanyService:
    """Dependency provider for CompanyService."""
    return CompanyService(session)


TenderServ = Annotated[TenderService, Depends(get_tender_service)]
CompanyServ = Annotated[CompanyService, Depends(get_company_service)]

router = APIRouter(prefix="/companies/{company_id}/tenders", tags=["tenders"])


@router.post("/", response_model=TenderResponse)
async def create_tender(
    company_id: int,
    tender: TenderCreateSchema,
    user: CurrentUser,
    tender_service: TenderServ,
    company_service: CompanyServ,
):
    await company_service.get_owned(company_id, user.id)
    return await tender_service.create(company_id, tender)


@router.get("/", response_model=TenderListSchema)
async def list_tenders(
    company_id: int,
    user: CurrentUser,
    tender_service: TenderServ,
    company_service: CompanyServ,
    tender_filter: Annotated[FilterTenderSchema, Query()],
):
    await company_service.get_owned(company_id, user.id)
    tenders = await tender_service.list(company_id, tender_filter)
    return {"tenders": tenders}


@router.patch("/{tender_id}", response_model=TenderResponse)
async def patch_tender(
    company_id: int,
    tender_id: int,
    tender: TenderUpdateSchema,
    user: CurrentUser,
    tender_service: TenderServ,
    company_service: CompanyServ,
):
    await company_service.get_owned(company_id, user.id)
    return await tender_service.update(tender_id, company_id, tender)


@router.delete("/{tender_id}", response_model=MessageSchema)
async def delete_tender(
    company_id: int,
    tender_id: int,
    user: CurrentUser,
    tender_service: TenderServ,
    company_service: CompanyServ,
):
    await company_service.get_owned(company_id, user.id)
    await tender_service.delete(tender_id, company_id)
    return {"message": "Tender has been deleted successfully."}
