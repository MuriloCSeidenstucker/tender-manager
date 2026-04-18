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
from src.schemas.tender import TenderCreateSchema, TenderUpdateSchema


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
        data: TenderCreateSchema | TenderUpdateSchema,
        exclude_tender_id: int | None = None,
    ):
        query = select(TenderEntity).where(
            TenderEntity.company_id == company_id,
            TenderEntity.tender_number == data.tender_number,
            TenderEntity.tender_year == data.tender_year,
            TenderEntity.public_body_name == data.public_body_name,
            TenderEntity.modality == data.modality,
            TenderEntity.format == data.format,
        )

        if exclude_tender_id is not None:
            query = query.where(TenderEntity.id != exclude_tender_id)

        existing_tender = await self.session.scalar(query)
        if existing_tender:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Uma licitação com esses dados já está cadastrada para esta empresa.",
            )

    async def create(self, company_id: int, data):
        await self._check_uniqueness(company_id=company_id, data=data)

        tender_data = data.model_dump()
        await self._validate_business_rules(tender_data)

        status = tender_data.pop("status", None) or TenderStatus.MONITORING
        tender_data.setdefault("participation_result", None)
        tender_data.setdefault("awarded_value", None)

        tender = TenderEntity(
            **tender_data,
            status=status,
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

    async def update(self, tender_id: int, company_id: int, data: TenderUpdateSchema):
        tender = await self._get_owned(tender_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        new_tender_number = update_data.get("tender_number", tender.tender_number)
        new_tender_year = update_data.get("tender_year", tender.tender_year)
        new_public_body_name = update_data.get(
            "public_body_name", tender.public_body_name
        )
        new_modality = update_data.get("modality", tender.modality)
        new_format = update_data.get("format", tender.format)

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
            or new_format != tender.format
        ):
            # Create a synthetic data object to pass to _check_uniqueness
            check_data = TenderUpdateSchema(
                tender_number=new_tender_number,
                tender_year=new_tender_year,
                public_body_name=new_public_body_name,
                modality=new_modality,
                format=new_format,
            )
            await self._check_uniqueness(
                company_id=company_id, data=check_data, exclude_tender_id=tender.id
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

        try:
            await self.session.delete(tender)
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Cannot delete tender due to database integrity constraints.",
            ) from e
