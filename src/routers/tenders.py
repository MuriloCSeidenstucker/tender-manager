from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import CompanyEntity, TenderEntity, TenderStatus, UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas import (
    FilterTenderSchema,
    TenderCreateSchema,
    TenderListSchema,
    TenderPublicSchema,
)
from src.security import get_current_user

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
    company = await session.scalar(
        select(CompanyEntity).where(
            CompanyEntity.id == company_id,
            CompanyEntity.user_id == user.id,
        )
    )

    if not company:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Company not found.",
        )

    db_tender = TenderEntity(
        tender_number=tender.tender_number,
        tender_year=tender.tender_year,
        object_description=tender.object_description,
        public_body_name=tender.public_body_name,
        modality=tender.modality,
        format=tender.format,
        status=TenderStatus.MONITORING,
        participation_result=None,
        awarded_value=None,
        session_date=tender.session_date,
        company_id=company.id,
    )

    session.add(db_tender)
    await session.commit()
    await session.refresh(db_tender)

    return db_tender


@router.get("/", response_model=TenderListSchema)
async def list_tenders(
    company_id: int,
    session: Session,
    user: CurrentUser,
    tender_filter: Annotated[FilterTenderSchema, Query()],
):
    # 🔒 Garantia de ownership
    company = await session.scalar(
        select(CompanyEntity).where(
            CompanyEntity.id == company_id,
            CompanyEntity.user_id == user.id,
        )
    )

    if not company:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Company not found.",
        )

    # 🔍 Query base
    query = select(TenderEntity).where(TenderEntity.company_id == company_id)

    # 🔧 Filtros dinâmicos (type-safe)
    if tender_filter.tender_number is not None:
        query = query.where(TenderEntity.tender_number == tender_filter.tender_number)

    if tender_filter.tender_year is not None:
        query = query.where(TenderEntity.tender_year == tender_filter.tender_year)

    if tender_filter.object_description:
        query = query.where(
            TenderEntity.object_description.ilike(
                f"%{tender_filter.object_description}%"
            )
        )

    if tender_filter.public_body_name:
        query = query.where(
            TenderEntity.public_body_name.ilike(f"%{tender_filter.public_body_name}%")
        )

    if tender_filter.modality:
        query = query.where(TenderEntity.modality == tender_filter.modality)

    if tender_filter.format:
        query = query.where(TenderEntity.format == tender_filter.format)

    if tender_filter.status:
        query = query.where(TenderEntity.status == tender_filter.status)

    if tender_filter.participation_result:
        query = query.where(
            TenderEntity.participation_result == tender_filter.participation_result
        )

    if tender_filter.session_date:
        query = query.where(TenderEntity.session_date == tender_filter.session_date)

    # 📄 Paginação
    result = await session.scalars(
        query.offset(tender_filter.offset).limit(tender_filter.limit)
    )

    tenders = result.all()

    return {"tenders": tenders}
