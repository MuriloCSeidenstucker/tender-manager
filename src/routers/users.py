from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.infra.settings.database import get_session
from src.schemas.common import FilterPageSchema, MessageSchema
from src.schemas.user import (
    UserCreateSchema,
    UserListSchema,
    UserPasswordUpdateSchema,
    UserPublicSchema,
    UserUpdateSchema,
)
from src.security import get_current_user
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
async def create_user(user: UserCreateSchema, session: Session):
    return await UserService(session).create(user)


@router.get("/", response_model=UserListSchema)
async def read_users(
    session: Session, filter_users: Annotated[FilterPageSchema, Query()]
):
    users = await UserService(session).list(filter_users)
    return {"users": users}


@router.patch("/{user_id}", response_model=UserPublicSchema)
async def update_user(
    user_id: int,
    user: UserUpdateSchema,
    session: Session,
    current_user: CurrentUser,
):
    return await UserService(session).update(user_id, current_user, user)


@router.patch("/{user_id}/password", response_model=MessageSchema)
async def update_password(
    user_id: int,
    passwords: UserPasswordUpdateSchema,
    session: Session,
    current_user: CurrentUser,
):
    await UserService(session).update_password(user_id, current_user, passwords)
    return {"message": "Password updated successfully"}


@router.delete("/{user_id}", response_model=MessageSchema)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    await UserService(session).delete(user_id, current_user)
    return {"message": "User deleted"}
