from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import CompanyEntity, TenderEntity, TenderStatus, UserEntity
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

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]

router = APIRouter(prefix="/companies/{company_id}/tenders", tags=["tenders"])


async def _get_company_owned_by_user(
    company_id: int, user_id: int, session: AsyncSession
):
    company = await session.scalar(
        select(CompanyEntity).where(
            CompanyEntity.id == company_id,
            CompanyEntity.user_id == user_id,
        )
    )
    if not company:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Company not found.",
        )
    return company


@router.post("/", response_model=TenderPublicSchema)
async def create_tender(
    company_id: int,
    tender: TenderCreateSchema,
    user: CurrentUser,
    session: Session,
):
    company = await _get_company_owned_by_user(company_id, user.id, session)

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
    await _get_company_owned_by_user(company_id, user.id, session)

    query = select(TenderEntity).where(TenderEntity.company_id == company_id)

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

    result = await session.scalars(
        query.offset(tender_filter.offset).limit(tender_filter.limit)
    )

    tenders = result.all()

    return {"tenders": tenders}


@router.patch("/{tender_id}", response_model=TenderPublicSchema)
async def patch_tender(
    company_id: int,
    tender_id: int,
    tender: TenderUpdateSchema,
    user: CurrentUser,
    session: Session,
):
    await _get_company_owned_by_user(
        company_id=company_id, user_id=user.id, session=session
    )

    db_tender = await session.scalar(
        select(TenderEntity).where(
            TenderEntity.id == tender_id,
            TenderEntity.company_id == company_id,
        )
    )

    if not db_tender:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Tender not found.",
        )

    for key, value in tender.model_dump(exclude_unset=True).items():
        setattr(db_tender, key, value)

    session.add(db_tender)
    await session.commit()
    await session.refresh(db_tender)

    return db_tender


@router.delete("/{tender_id}", response_model=MessageSchema)
async def delete_tender(
    company_id: int,
    tender_id: int,
    user: CurrentUser,
    session: Session,
):
    await _get_company_owned_by_user(
        company_id=company_id, user_id=user.id, session=session
    )

    db_tender = await session.scalar(
        select(TenderEntity).where(
            TenderEntity.id == tender_id,
            TenderEntity.company_id == company_id,
        )
    )

    if not db_tender:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Tender not found.",
        )

    await session.delete(db_tender)
    await session.commit()

    return {"message": "Tender has been deleted successfully."}
