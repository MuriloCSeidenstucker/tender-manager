from dataclasses import asdict

from sqlalchemy import select

from src.infra.entities.user_entity import UserEntity


def test_create_user(session, mock_db_time):
    with mock_db_time(model=UserEntity) as time:
        new_user = UserEntity(username="alice", password="secret", email="test@test")
        session.add(new_user)
        session.commit()

    user = session.scalar(select(UserEntity).where(UserEntity.username == "alice"))

    assert asdict(user) == {
        "id": 1,
        "username": "alice",
        "password": "secret",
        "email": "test@test",
        "created_at": time,
    }
