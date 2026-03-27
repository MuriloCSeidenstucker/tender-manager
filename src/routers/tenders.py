from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import CompanyEntity, TenderEntity, TenderStatus, UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas import TenderCreateSchema, TenderPublicSchema
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
