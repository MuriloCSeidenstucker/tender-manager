from decimal import Decimal
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.infra.entities import ParticipationResult, TenderStatus
from src.schemas.tender import TenderCreateSchema, TenderUpdateSchema
from src.services.tender_service import TenderService
from tests.factories import CompanyFactory, TenderFactory


@pytest.mark.asyncio
async def test_tender_service_create_with_duplicate_data_raises_conflict(session, user):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    existing = TenderFactory(
        company_id=company.id,
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
    )
    session.add(existing)
    await session.commit()

    data = TenderCreateSchema(
        tender_number=123,
        tender_year=2026,
        object_description="Valid object description",
        public_body_name="City Hall",
        modality=existing.modality,
        format=existing.format,
        session_date=existing.session_date,
    )

    with pytest.raises(HTTPException) as exc:
        await service.create(company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_tender_service_update_won_tender_without_awarded_value_raises_unprocessable(
    session,
    user,
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()

    data = TenderUpdateSchema(
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("0.0"),
    )

    with pytest.raises(HTTPException) as exc:
        await service.update(tender.id, company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_tender_service_update_with_duplicate_data_raises_conflict(session, user):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    tender_1 = TenderFactory(
        company_id=company.id,
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
    )
    tender_2 = TenderFactory(
        company_id=company.id,
        tender_number=456,
        tender_year=2027,
        public_body_name="Health Department",
        modality="trading_session",
    )
    session.add_all([tender_1, tender_2])
    await session.commit()

    data = TenderUpdateSchema(
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
    )

    with pytest.raises(HTTPException) as exc:
        await service.update(tender_2.id, company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_tender_service_update_with_same_identity_values_succeeds(session, user):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    tender = TenderFactory(
        company_id=company.id,
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
        status=TenderStatus.FINISHED,
    )
    duplicate = TenderFactory(
        company_id=company.id,
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
        status=TenderStatus.FINISHED,
    )
    session.add_all([tender, duplicate])
    await session.commit()

    data = TenderUpdateSchema(
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("1.0"),
    )

    updated = await service.update(tender.id, company_id=company.id, data=data)

    assert updated.id == tender.id
    assert updated.participation_result == ParticipationResult.WON


@pytest.mark.asyncio
async def test_tender_service_create_with_integrity_error_raises_conflict(
    session, user
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    data = TenderCreateSchema(
        tender_number=123,
        tender_year=2026,
        object_description="Valid object description",
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
    )

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.create(company.id, data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_tender_service_update_with_integrity_error_raises_conflict(
    session, user
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()

    data = TenderUpdateSchema(object_description="Updated")

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.update(tender.id, company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_tender_service_list_with_filters_returns_matching_tenders(session, user):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()

    filters = SimpleNamespace(
        tender_number=tender.tender_number,
        tender_year=tender.tender_year,
        object_description=(
            tender.object_description[:3] if tender.object_description else None
        ),
        public_body_name=(
            tender.public_body_name[:3] if tender.public_body_name else None
        ),
        modality=tender.modality,
        format=tender.format,
        status=tender.status,
        participation_result=tender.participation_result,
        session_date=tender.session_date,
        offset=0,
        limit=10,
    )

    result = await service.list(company.id, filters)
    assert len(result) == 1
    assert result[0].id == tender.id


@pytest.mark.parametrize("status", list(TenderStatus))
@pytest.mark.asyncio
async def test_tender_service_create_with_various_statuses_persists_status_correctly(
    session, user, status
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    data = TenderCreateSchema(
        tender_number=123,
        tender_year=2026,
        object_description="Valid object description",
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
        status=status,
    )

    created = await service.create(company.id, data)

    assert created.status == status
    assert created.company_id == company.id


@pytest.mark.asyncio
async def test_tender_service_create_won_tender_without_awarded_value_raises_unprocessable(
    session,
    user,
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    data = TenderCreateSchema(
        tender_number=789,
        tender_year=2026,
        object_description="Valid object description",
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
        status=TenderStatus.FINISHED,
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("0.0"),
    )

    with pytest.raises(HTTPException) as exc:
        await service.create(company.id, data)

    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_tender_service_create_won_tender_with_positive_awarded_value_succeeds(
    session,
    user,
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    data = TenderCreateSchema(
        tender_number=999,
        tender_year=2026,
        object_description="Valid object description",
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
        status=TenderStatus.FINISHED,
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("1500.50"),
    )

    created = await service.create(company.id, data)
    assert created.participation_result == ParticipationResult.WON
    assert float(created.awarded_value) == 1500.50


@pytest.mark.parametrize(
    "field_to_change,new_value",
    [
        ("tender_number", 999),
        ("tender_year", 2027),
        ("public_body_name", "Different City Hall"),
        ("modality", "auction"),
        ("format", "in_person"),
    ],
)
@pytest.mark.asyncio
async def test_tender_service_uniqueness_check_with_different_key_fields_passes(
    session, user, field_to_change, new_value
):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    existing = TenderFactory(
        company_id=company.id,
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
        format="electronic",
    )
    session.add(existing)
    await session.commit()

    data_args = {
        "tender_number": 123,
        "tender_year": 2026,
        "object_description": "Valid description",
        "public_body_name": "City Hall",
        "modality": "trading_session",
        "format": "electronic",
    }
    data_args[field_to_change] = new_value

    data = TenderCreateSchema(**data_args)

    created = await service.create(company_id=company.id, data=data)
    assert created.id is not None
