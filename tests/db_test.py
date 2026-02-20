from dataclasses import asdict

import pytest
from sqlalchemy import select

from src.infra.entities import TodoEntity, UserEntity


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
        "todos": [],
    }


@pytest.mark.asyncio
async def test_creat_todo(session, user):
    todo = TodoEntity(
        title="Test Todo",
        description="Test Desc",
        state="draft",
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(TodoEntity))

    assert asdict(todo) == {
        "description": "Test Desc",
        "id": 1,
        "state": "draft",
        "title": "Test Todo",
        "user_id": 1,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: UserEntity):
    todo = TodoEntity(
        title="Test Todo",
        description="Test Desc",
        state="draft",
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(UserEntity).where(UserEntity.id == user.id))

    assert user.todos == [todo]
