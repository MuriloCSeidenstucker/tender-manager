from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.security import get_password_hash, verify_password


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

        hashed_password = await get_password_hash(data.password)

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

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(current_user, key, value)

        try:
            await self.session.commit()
            await self.session.refresh(current_user)

            return current_user

        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username or Email already exists",
            ) from e

    async def update_password(self, user_id: int, current_user: UserEntity, data):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
            )

        if not await verify_password(data.current_password, current_user.password):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="Invalid current password",
            )

        current_user.password = await get_password_hash(data.new_password)
        await self.session.commit()
        await self.session.refresh(current_user)

    async def delete(self, user_id: int, current_user: UserEntity):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
            )

        await self.session.delete(current_user)
        await self.session.commit()
