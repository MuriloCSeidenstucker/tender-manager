from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.infra.settings.database import get_session
from src.schemas.common import MessageSchema
from src.schemas.company import (
    CompanyCreateSchema,
    CompanyListSchema,
    CompanyPublicSchema,
    CompanyUpdateSchema,
    FilterCompanySchema,
)
from src.security import get_current_user
from src.services.company_service import CompanyService

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyPublicSchema, status_code=HTTPStatus.CREATED)
async def create_company(
    company: CompanyCreateSchema,
    user: CurrentUser,
    session: Session,
):
    service = CompanyService(session)
    return await service.create(user.id, company)


@router.get("/", response_model=CompanyListSchema)
async def list_companies(
    session: Session,
    user: CurrentUser,
    company_filter: Annotated[FilterCompanySchema, Query()],
):
    service = CompanyService(session)
    companies = await service.list(user.id, company_filter)
    return {"companies": companies}


@router.patch("/{company_id}", response_model=CompanyPublicSchema)
async def patch_company(
    company_id: int, session: Session, user: CurrentUser, company: CompanyUpdateSchema
):
    service = CompanyService(session)
    return await service.update(company_id, user.id, company)


@router.delete("/{company_id}", response_model=MessageSchema)
async def delete_company(company_id: int, session: Session, user: CurrentUser):
    service = CompanyService(session)
    await service.delete(company_id, user.id)

    return {"message": "Company has been deleted successfully."}
