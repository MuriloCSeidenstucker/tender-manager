from dataclasses import asdict

import pytest
from sqlalchemy import select

from src.infra.entities import CompanyEntity, UserEntity


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=UserEntity) as time:
        new_user = UserEntity(username="alice", password="secret", email="test@test")
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(UserEntity).where(UserEntity.username == "alice")
    )

    assert asdict(user) == {
        "id": 1,
        "username": "alice",
        "password": "secret",
        "email": "test@test",
        "created_at": time,
        "companies": [],
    }


@pytest.mark.asyncio
async def test_create_company(session, user):
    company = CompanyEntity(
        name="Test Company",
        trade_name="Test trade name",
        cnpj="12345678901234",
        user_id=user.id,
    )

    session.add(company)
    await session.commit()

    company = await session.scalar(select(CompanyEntity))

    assert company.id == 1
    assert company.name == "Test Company"
    assert company.trade_name == "Test trade name"
    assert company.cnpj == "12345678901234"
    assert company.user_id == user.id
    assert company.created_at is not None


@pytest.mark.asyncio
async def test_user_company_relationship(session, user: UserEntity):
    company = CompanyEntity(
        name="Test Company",
        trade_name="Test trade name",
        cnpj="12345678901234",
        user_id=user.id,
    )

    session.add(company)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(UserEntity).where(UserEntity.id == user.id))

    assert user.companies == [company]
