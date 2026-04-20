# pylint: disable=W0613:unused-argument
from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.services.user_service import UserService
from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_user_service_create_with_duplicate_username_raises_conflict(session):
    service = UserService(session)
    existing_user = UserFactory(username="duplicate")
    session.add(existing_user)
    await session.commit()

    class DummyData:
        username = "duplicate"
        email = "other@test.com"
        password = "password"

    with pytest.raises(HTTPException) as exc:
        await service.create(DummyData())

    assert exc.value.status_code == HTTPStatus.CONFLICT
    assert exc.value.detail == "Username already exists"


@pytest.mark.asyncio
async def test_user_service_create_with_duplicate_email_raises_conflict(session):
    service = UserService(session)
    existing_user = UserFactory(email="duplicate@test.com")
    session.add(existing_user)
    await session.commit()

    class DummyData:
        username = "other"
        email = "duplicate@test.com"
        password = "password"

    with pytest.raises(HTTPException) as exc:
        await service.create(DummyData())

    assert exc.value.status_code == HTTPStatus.CONFLICT
    assert exc.value.detail == "Email already exists"


@pytest.mark.asyncio
async def test_user_service_update_another_user_raises_forbidden(
    session, user, other_user
):
    service = UserService(session)

    class DummyData:
        def model_dump(self, exclude_unset=True):
            return {"username": "newname"}

    with pytest.raises(HTTPException) as exc:
        await service.update(user_id=other_user.id, current_user=user, data=DummyData())

    assert exc.value.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_user_service_update_password_with_invalid_current_raises_unprocessable(
    session, user
):
    service = UserService(session)

    class DummyData:
        current_password = "wrongpassword"
        new_password = "newpassword"

    with pytest.raises(HTTPException) as exc:
        await service.update_password(
            user_id=user.id, current_user=user, data=DummyData()
        )

    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert exc.value.detail == "Invalid current password"


@pytest.mark.asyncio
async def test_user_service_update_password_with_wrong_user_raises_forbidden(
    session, user, other_user
):
    service = UserService(session)

    class DummyData:
        current_password = "any"
        new_password = "any"

    with pytest.raises(HTTPException) as exc:
        await service.update_password(
            user_id=other_user.id, current_user=user, data=DummyData()
        )

    assert exc.value.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_user_service_delete_another_user_raises_forbidden(
    session, user, other_user
):
    service = UserService(session)

    with pytest.raises(HTTPException) as exc:
        await service.delete(user_id=other_user.id, current_user=user)

    assert exc.value.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_user_service_update_with_integrity_error_raises_conflict(session, user):
    service = UserService(session)

    class DummyData:
        def model_dump(self, exclude_unset=True):
            return {"username": "error"}

    session.commit = AsyncMock(side_effect=IntegrityError("x", "y", "z"))

    with pytest.raises(HTTPException) as exc:
        await service.update(user_id=user.id, current_user=user, data=DummyData())

    assert exc.value.status_code == HTTPStatus.CONFLICT
