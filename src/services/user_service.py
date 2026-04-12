from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.security import get_password_hash


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data):
        db_user = await self.session.scalar(
            select(UserEntity).where(
                (UserEntity.username == data.username)
                | (UserEntity.email == data.email)
            )
        )

        if db_user:
            if db_user.username == data.username:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail="Username already exists",
                )
            if db_user.email == data.email:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail="Email already exists",
                )

        hashed_password = get_password_hash(data.password)

        new_user = UserEntity(
            email=data.email,
            username=data.username,
            password=hashed_password,
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def list(self, filters):
        query = await self.session.scalars(
            select(UserEntity).offset(filters.offset).limit(filters.limit)
        )
        return query.all()

    async def update(self, user_id: int, current_user: UserEntity, data):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
            )

        try:
            current_user.username = data.username
            current_user.password = get_password_hash(data.password)
            current_user.email = data.email

            await self.session.commit()
            await self.session.refresh(current_user)

            return current_user

        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username or Email already exists",
            ) from e

    async def delete(self, user_id: int, current_user: UserEntity):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
            )

        await self.session.delete(current_user)
        await self.session.commit()
