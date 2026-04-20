# pylint: disable=W0613:unused-argument

from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.services.company_service import CompanyService
from tests.factories import CompanyFactory


@pytest.mark.asyncio
async def test_company_service_create_with_valid_data_returns_company(session, user):
    service = CompanyService(session)

    data = CompanyFactory.build(user_id=user.id)

    company = await service.create(user.id, data)

    assert company.id is not None
    assert company.name == data.name


@pytest.mark.asyncio
async def test_company_service_create_with_duplicate_name_raises_conflict(
    session, user
):
    service = CompanyService(session)

    existing = CompanyFactory(user_id=user.id, name="duplicate")
    session.add(existing)
    await session.commit()

    data = CompanyFactory.build(user_id=user.id, name="duplicate")

    with pytest.raises(HTTPException) as exc:
        await service.create(user.id, data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_company_service_get_owned_with_nonexistent_id_raises_not_found(
    session, user
):
    service = CompanyService(session)

    with pytest.raises(HTTPException) as exc:
        await service.get_owned(company_id=999, user_id=user.id)

    assert exc.value.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_company_service_get_owned_with_wrong_user_raises_not_found(
    session, user, other_user
):
    service = CompanyService(session)

    company = CompanyFactory(user_id=other_user.id)
    session.add(company)
    await session.commit()

    with pytest.raises(HTTPException):
        await service.get_owned(company.id, user.id)


@pytest.mark.asyncio
async def test_company_service_update_with_valid_data_updates_name(session, user):
    service = CompanyService(session)

    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    class Dummy:
        def model_dump(self, exclude_unset=True):
            return {"name": "updated"}

    updated = await service.update(company.id, user.id, Dummy())

    assert updated.name == "updated"


@pytest.mark.asyncio
async def test_company_service_delete_with_nonexistent_id_raises_not_found(
    session, user
):
    service = CompanyService(session)

    with pytest.raises(HTTPException):
        await service.delete(999, user.id)


@pytest.mark.asyncio
async def test_company_service_create_with_duplicate_cnpj_raises_conflict(
    session, user
):
    service = CompanyService(session)

    existing = CompanyFactory(user_id=user.id, cnpj="12345678901234")
    session.add(existing)
    await session.commit()

    data = CompanyFactory.build(user_id=user.id, cnpj="12345678901234")

    with pytest.raises(HTTPException) as exc:
        await service.create(user.id, data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_company_service_create_with_integrity_error_raises_conflict(
    session, user
):
    service = CompanyService(session)

    data = CompanyFactory.build(user_id=user.id)

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.create(user.id, data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_company_service_update_with_integrity_error_raises_conflict(
    session, user
):
    service = CompanyService(session)

    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    class Dummy:
        def model_dump(self, exclude_unset=True):
            return {"name": "updated"}

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.update(company.id, user.id, Dummy())

    assert exc.value.status_code == HTTPStatus.CONFLICT
