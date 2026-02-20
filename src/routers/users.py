# pylint: disable=R1720:no-else-raise

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas import (
    FilterPageSchema,
    MessageSchema,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)
from src.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["users"])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
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
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get("/", response_model=UserListSchema)
async def read_users(
    session: Session, filter_users: Annotated[FilterPageSchema, Query()]
):
    query = await session.scalars(
        select(UserEntity).offset(filter_users.offset).limit(filter_users.limit)
    )
    users = query.all()

    return {"users": users}


@router.put("/{user_id}", response_model=UserPublicSchema)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
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
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        ) from e


@router.delete("/{user_id}", response_model=MessageSchema)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    await session.delete(current_user)
    await session.commit()

    return {"message": "User deleted"}
