# pylint: disable=R1720:no-else-raise

from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infra.entities.user_entity import UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas.user_schema import (
    Message,
    UserList,
    UserPublicSchema,
    UserSchema,
)

app = FastAPI()


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(UserEntity).where(
            (UserEntity.username == user.username) | (UserEntity.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    db_user = UserEntity(
        username=user.username, password=user.password, email=user.email
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get("/users/", response_model=UserList)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(UserEntity).offset(skip).limit(limit)).all()
    return {"users": users}


@app.put("/users/{user_id}", response_model=UserPublicSchema)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(UserEntity).where(UserEntity.id == user_id))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    try:
        db_user.username = user.username
        db_user.password = user.password
        db_user.email = user.email
        session.commit()
        session.refresh(db_user)

        return db_user

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Username or Email already exists"
        ) from e


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(UserEntity).where(UserEntity.id == user_id))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    session.delete(db_user)
    session.commit()

    return {"message": "User deleted"}
