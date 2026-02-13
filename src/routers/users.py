# pylint: disable=R1720:no-else-raise

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infra.entities.user_entity import UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas.user_schema import (
    FilterPage,
    Message,
    UserList,
    UserPublicSchema,
    UserSchema,
)
from src.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["users"])
AnnotatedSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
def create_user(user: UserSchema, session: AnnotatedSession):
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

    hashed_password = get_password_hash(user.password)

    db_user = UserEntity(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get("/", response_model=UserList)
def read_users(session: AnnotatedSession, filter_users: Annotated[FilterPage, Query()]):
    users = session.scalars(
        select(UserEntity).offset(filter_users.offset).limit(filter_users.limit)
    ).all()

    return {"users": users}


@router.put("/{user_id}", response_model=UserPublicSchema)
def update_user(
    user_id: int,
    user: UserSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )
    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        ) from e


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    session.delete(current_user)
    session.commit()

    return {"message": "User deleted"}
