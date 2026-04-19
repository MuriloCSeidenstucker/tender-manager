from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import TenderEntity
from src.schemas.tender import TenderCreateSchema, TenderUpdateSchema
from src.services.validators.tender_validator import TenderValidator


class TenderService:
    """
    Service layer for managing Procurement Tenders (Licitações).
    Orchestrates business logic, validation, and database persistence.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _find_by_id_and_company(self, tender_id: int, company_id: int):
        """
        Finds a tender by ID and ensures it belongs to the given company.
        """
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

    async def _verify_uniqueness(
        self,
        company_id: int,
        tender_number: int,
        tender_year: int,
        public_body_name: str,
        modality,
        format,
        exclude_tender_id: int | None = None,
    ) -> None:
        """
        Ensures that no duplicate tender exists for the same company with the same core data.
        """
        query = select(TenderEntity).where(
            TenderEntity.company_id == company_id,
            TenderEntity.tender_number == tender_number,
            TenderEntity.tender_year == tender_year,
            TenderEntity.public_body_name == public_body_name,
            TenderEntity.modality == modality,
            TenderEntity.format == format,
        )

        if exclude_tender_id is not None:
            query = query.where(TenderEntity.id != exclude_tender_id)

        existing_tender = await self.session.scalar(query)
        if existing_tender:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A tender with these details is already registered for this company.",
            )

    async def create(self, company_id: int, data: TenderCreateSchema):
        """
        Creates a new tender after verifying uniqueness and business rules.
        """
        # 1. Verification
        await self._verify_uniqueness(
            company_id=company_id,
            tender_number=data.tender_number,
            tender_year=data.tender_year,
            public_body_name=data.public_body_name,
            modality=data.modality,
            format=data.format,
        )

        # 2. Domain Validation
        TenderValidator.validate_rules(
            participation_result=data.participation_result,
            awarded_value=data.awarded_value,
            status=data.status,
        )

        # 3. Persistence
        tender_data = data.model_dump()
        tender = TenderEntity(
            **tender_data,
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
        """
        Lists tenders for a specific company with optional filters.
        """
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
        """
        Updates an existing tender, validating new state against business rules.
        """
        tender = await self._find_by_id_and_company(tender_id, company_id)
        update_data = data.model_dump(exclude_unset=True)

        # 1. Domain Validation (merged state)
        new_result = update_data.get(
            "participation_result", tender.participation_result
        )
        new_value = update_data.get("awarded_value", tender.awarded_value)
        new_status = update_data.get("status", tender.status)

        TenderValidator.validate_rules(
            participation_result=new_result, awarded_value=new_value, status=new_status
        )

        # 2. Uniqueness check if needed
        id_fields = {
            "tender_number",
            "tender_year",
            "public_body_name",
            "modality",
            "format",
        }
        if any(field in update_data for field in id_fields):
            await self._verify_uniqueness(
                company_id=company_id,
                tender_number=update_data.get("tender_number", tender.tender_number),
                tender_year=update_data.get("tender_year", tender.tender_year),
                public_body_name=update_data.get(
                    "public_body_name", tender.public_body_name
                ),
                modality=update_data.get("modality", tender.modality),
                format=update_data.get("format", tender.format),
                exclude_tender_id=tender.id,
            )

        # 3. Object update
        for key, value in update_data.items():
            setattr(tender, key, value)

        self.session.add(tender)

        try:
            await self.session.commit()
            await self.session.refresh(tender)
        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Database integrity error.",
            ) from e

        return tender

    async def delete(self, tender_id: int, company_id: int):
        """
        Deletes a tender.
        """
        tender = await self._find_by_id_and_company(tender_id, company_id)

        try:
            await self.session.delete(tender)
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Cannot delete tender due to database integrity constraints.",
            ) from e
