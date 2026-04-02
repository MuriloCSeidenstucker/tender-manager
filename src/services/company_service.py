from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import CompanyEntity


class CompanyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, data):
        existing = await self.session.scalar(
            select(CompanyEntity).where(
                CompanyEntity.user_id == user_id,
                CompanyEntity.name == data.name,
            )
        )

        if existing:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Company name already exists for this user.",
            )

        company = CompanyEntity(
            name=data.name,
            trade_name=data.trade_name,
            cnpj=data.cnpj,
            user_id=user_id,
        )

        self.session.add(company)

        try:
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Database integrity error.",
            ) from e

        await self.session.refresh(company)
        return company

    async def get_owned(self, company_id: int, user_id: int):
        company = await self.session.scalar(
            select(CompanyEntity).where(
                CompanyEntity.id == company_id,
                CompanyEntity.user_id == user_id,
            )
        )

        if not company:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Company not found.",
            )

        return company

    async def list(self, user_id: int, filters):
        query = select(CompanyEntity).where(CompanyEntity.user_id == user_id)

        if filters.name:
            query = query.filter(CompanyEntity.name.contains(filters.name))

        if filters.trade_name:
            query = query.filter(CompanyEntity.trade_name.contains(filters.trade_name))

        if filters.cnpj:
            query = query.filter(CompanyEntity.cnpj == filters.cnpj)

        result = await self.session.scalars(
            query.offset(filters.offset).limit(filters.limit)
        )

        return result.all()

    async def update(self, company_id: int, user_id: int, data):
        company = await self.get_owned(company_id, user_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(company, key, value)

        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)

        return company

    async def delete(self, company_id: int, user_id: int):
        company = await self.get_owned(company_id, user_id)

        await self.session.delete(company)
        await self.session.commit()
