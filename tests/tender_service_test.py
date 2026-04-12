from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.infra.entities import ParticipationResult
from src.services.tender_service import TenderService
from tests.factories import CompanyFactory, TenderFactory


@pytest.mark.asyncio
async def test_create_tender_duplicate_should_raise_conflict(session, user):
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

    data = SimpleNamespace(
        tender_number=123,
        tender_year=2026,
        object_description="Valid object description",
        public_body_name="City Hall",
        modality=existing.modality,
        format=existing.format,
        session_date=existing.session_date,
        model_dump=lambda: {
            "tender_number": 123,
            "tender_year": 2026,
            "object_description": "Valid object description",
            "public_body_name": "City Hall",
            "modality": existing.modality,
            "format": existing.format,
            "session_date": existing.session_date,
        },
    )

    with pytest.raises(HTTPException) as exc:
        await service.create(company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_tender_won_without_positive_awarded_value_should_raise(
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

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "participation_result": ParticipationResult.WON,
            "awarded_value": 0,
        }
    )

    with pytest.raises(HTTPException) as exc:
        await service.update(tender.id, company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_tender_duplicate_should_raise_conflict(session, user):
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

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "tender_number": 123,
            "tender_year": 2026,
            "public_body_name": "City Hall",
        }
    )

    with pytest.raises(HTTPException) as exc:
        await service.update(tender_2.id, company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_tender_should_ignore_same_identification_values(session, user):
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
    )
    duplicate = TenderFactory(
        company_id=company.id,
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
    )
    session.add_all([tender, duplicate])
    await session.commit()

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "tender_number": 123,
            "tender_year": 2026,
            "public_body_name": "City Hall",
            "participation_result": ParticipationResult.WON,
            "awarded_value": 1,
        }
    )

    updated = await service.update(tender.id, company_id=company.id, data=data)

    assert updated.id == tender.id
    assert updated.participation_result == ParticipationResult.WON


@pytest.mark.asyncio
async def test_create_tender_integrity_error(session, user):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    data = SimpleNamespace(
        tender_number=123,
        tender_year=2026,
        public_body_name="City Hall",
        modality="trading_session",
        model_dump=lambda: {
            "tender_number": 123,
            "tender_year": 2026,
            "object_description": "Valid object description",
            "public_body_name": "City Hall",
            "modality": "trading_session",
            "format": "electronic",
            "session_date": "2026-01-01T10:00:00",
        },
    )

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.create(company.id, data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_tender_integrity_error(session, user):
    service = TenderService(session)
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {"object_description": "Updated"}
    )

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.update(tender.id, company_id=company.id, data=data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_list_tenders_with_filters(session, user):
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
