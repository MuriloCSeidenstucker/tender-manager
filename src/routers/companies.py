from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import CompanyEntity, UserEntity
from src.infra.settings.database import get_session
from src.schemas import (
    CompanyCreateSchema,
    CompanyListSchema,
    CompanyPublicSchema,
    CompanyUpdateSchema,
    FilterCompanySchema,
    MessageSchema,
)
from src.security import get_current_user

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyPublicSchema)
async def create_company(
    company: CompanyCreateSchema,
    user: CurrentUser,
    session: Session,
):
    db_company = CompanyEntity(
        name=company.name,
        trade_name=company.trade_name,
        cnpj=company.cnpj,
        user_id=user.id,
    )
    session.add(db_company)
    await session.commit()
    await session.refresh(db_company)

    return db_company


@router.get("/", response_model=CompanyListSchema)
async def list_companies(
    session: Session,
    user: CurrentUser,
    company_filter: Annotated[FilterCompanySchema, Query()],
):
    query = select(CompanyEntity).where(CompanyEntity.user_id == user.id)

    if company_filter.name:
        query = query.filter(CompanyEntity.name.contains(company_filter.name))

    if company_filter.trade_name:
        query = query.filter(
            CompanyEntity.trade_name.contains(company_filter.trade_name)
        )

    if company_filter.cnpj:
        query = query.filter(CompanyEntity.cnpj == company_filter.cnpj)

    companies = await session.scalars(
        query.offset(company_filter.offset).limit(company_filter.limit)
    )

    return {"companies": companies.all()}


@router.patch("/{company_id}", response_model=CompanyPublicSchema)
async def patch_company(
    company_id: int, session: Session, user: CurrentUser, company: CompanyUpdateSchema
):
    db_company = await session.scalar(
        select(CompanyEntity).where(
            CompanyEntity.user_id == user.id, CompanyEntity.id == company_id
        )
    )

    if not db_company:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Company not found."
        )

    for key, value in company.model_dump(exclude_unset=True).items():
        setattr(db_company, key, value)

    session.add(db_company)
    await session.commit()
    await session.refresh(db_company)

    return db_company


@router.delete("/{company_id}", response_model=MessageSchema)
async def delete_company(company_id: int, session: Session, user: CurrentUser):
    company = await session.scalar(
        select(CompanyEntity).where(
            CompanyEntity.user_id == user.id, CompanyEntity.id == company_id
        )
    )

    if not company:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Company not found."
        )

    await session.delete(company)
    await session.commit()

    return {"message": "Company has been deleted successfully."}
