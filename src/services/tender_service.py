# pylint: disable=R0917:too-many-positional-arguments

from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import (
    ParticipationResult,
    TenderEntity,
    TenderStatus,
)


class TenderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_owned(self, tender_id: int, company_id: int):
        tender = await self.session.scalar(
            select(TenderEntity).where(
                TenderEntity.id == tender_id,
                TenderEntity.company_id == company_id,
            )
        )

        if not tender:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Tender not found.",
            )

        return tender

    async def _validate_business_rules(self, data):
        awarded_value = data.get("awarded_value")

        if data.get("participation_result") == ParticipationResult.WON and (
            awarded_value is None or awarded_value <= 0
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=(
                    "Awarded value must be greater than zero when "
                    "participation result is WON."
                ),
            )

    async def _check_uniqueness(
        self,
        company_id: int,
        tender_number: int,
        tender_year: int,
        public_body_name: str,
        modality: str,
        exclude_id: int | None = None,
    ):
        query = select(TenderEntity).where(
            TenderEntity.company_id == company_id,
            TenderEntity.tender_number == tender_number,
            TenderEntity.tender_year == tender_year,
            TenderEntity.public_body_name == public_body_name,
            TenderEntity.modality == modality,
        )

        if exclude_id:
            query = query.where(TenderEntity.id != exclude_id)

        existing = await self.session.scalar(query)

        if existing:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Tender already exists for this company, public body, and modality.",
            )

    async def create(self, company_id: int, data):
        await self._check_uniqueness(
            company_id=company_id,
            tender_number=data.tender_number,
            tender_year=data.tender_year,
            public_body_name=data.public_body_name,
            modality=data.modality,
        )

        tender = TenderEntity(
            **data.model_dump(),
            status=TenderStatus.MONITORING,
            participation_result=None,
            awarded_value=None,
            company_id=company_id,
        )

        self.session.add(tender)

        try:
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Database integrity error.",
            ) from e

        await self.session.refresh(tender)
        return tender

    async def list(self, company_id: int, filters):
        query = select(TenderEntity).where(TenderEntity.company_id == company_id)

        if filters.tender_number is not None:
            query = query.where(TenderEntity.tender_number == filters.tender_number)

        if filters.tender_year is not None:
            query = query.where(TenderEntity.tender_year == filters.tender_year)

        if filters.object_description:
            query = query.where(
                TenderEntity.object_description.ilike(f"%{filters.object_description}%")
            )

        if filters.public_body_name:
            query = query.where(
                TenderEntity.public_body_name.ilike(f"%{filters.public_body_name}%")
            )

        if filters.modality:
            query = query.where(TenderEntity.modality == filters.modality)

        if filters.format:
            query = query.where(TenderEntity.format == filters.format)

        if filters.status:
            query = query.where(TenderEntity.status == filters.status)

        if filters.participation_result:
            query = query.where(
                TenderEntity.participation_result == filters.participation_result
            )

        if filters.session_date:
            query = query.where(TenderEntity.session_date == filters.session_date)

        result = await self.session.scalars(
            query.offset(filters.offset).limit(filters.limit)
        )

        return result.all()

    async def update(self, tender_id: int, company_id: int, data):
        tender = await self._get_owned(tender_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        new_tender_number = update_data.get("tender_number", tender.tender_number)
        new_tender_year = update_data.get("tender_year", tender.tender_year)
        new_public_body_name = update_data.get(
            "public_body_name", tender.public_body_name
        )
        new_modality = update_data.get("modality", tender.modality)

        await self._validate_business_rules(
            {
                "participation_result": update_data.get(
                    "participation_result", tender.participation_result
                ),
                "awarded_value": update_data.get("awarded_value", tender.awarded_value),
            }
        )

        if (
            new_tender_number != tender.tender_number
            or new_tender_year != tender.tender_year
            or new_public_body_name != tender.public_body_name
            or new_modality != tender.modality
        ):
            await self._check_uniqueness(
                company_id=company_id,
                tender_number=new_tender_number,
                tender_year=new_tender_year,
                public_body_name=new_public_body_name,
                modality=new_modality,
                exclude_id=tender.id,
            )

        for key, value in update_data.items():
            setattr(tender, key, value)

        self.session.add(tender)

        try:
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Database integrity error.",
            ) from e

        await self.session.refresh(tender)
        return tender

    async def delete(self, tender_id: int, company_id: int):
        tender = await self._get_owned(tender_id, company_id)

        await self.session.delete(tender)
        await self.session.commit()
