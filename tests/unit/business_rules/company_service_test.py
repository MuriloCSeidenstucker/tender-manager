# pylint: disable=W0613:unused-argument

from http import HTTPStatus

import pytest
from fastapi import HTTPException

from src.services.company_service import CompanyService
from tests.factories import CompanyFactory


@pytest.mark.asyncio
async def test_create_company_success(session, user):
    service = CompanyService(session)

    data = CompanyFactory.build(user_id=user.id)

    company = await service.create(user.id, data)

    assert company.id is not None
    assert company.name == data.name


@pytest.mark.asyncio
async def test_create_company_duplicate_name(session, user):
    service = CompanyService(session)

    existing = CompanyFactory(user_id=user.id, name="duplicate")
    session.add(existing)
    await session.commit()

    data = CompanyFactory.build(user_id=user.id, name="duplicate")

    with pytest.raises(HTTPException) as exc:
        await service.create(user.id, data)

    assert exc.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_get_owned_not_found(session, user):
    service = CompanyService(session)

    with pytest.raises(HTTPException) as exc:
        await service.get_owned(company_id=999, user_id=user.id)

    assert exc.value.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_owned_wrong_user(session, user, other_user):
    service = CompanyService(session)

    company = CompanyFactory(user_id=other_user.id)
    session.add(company)
    await session.commit()

    with pytest.raises(HTTPException):
        await service.get_owned(company.id, user.id)


@pytest.mark.asyncio
async def test_update_company(session, user):
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
async def test_delete_company_not_found(session, user):
    service = CompanyService(session)

    with pytest.raises(HTTPException):
        await service.delete(999, user.id)
