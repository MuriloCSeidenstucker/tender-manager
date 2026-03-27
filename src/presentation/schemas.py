from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.infra.entities import (
    ParticipationResult,
    TenderFormat,
    TenderModality,
    TenderStatus,
)


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]


class MessageSchema(BaseModel):
    message: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class FilterPageSchema(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


class CompanyCreateSchema(BaseModel):
    name: str
    trade_name: str
    cnpj: str


class CompanyPublicSchema(CompanyCreateSchema):
    id: int


class CompanyListSchema(BaseModel):
    companies: list[CompanyPublicSchema]


class FilterCompanySchema(FilterPageSchema):
    name: str | None = Field(None, min_length=3, max_length=150)
    trade_name: str | None = Field(None, min_length=3, max_length=150)
    cnpj: str | None = Field(None, min_length=5, max_length=14)


class CompanyUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=150)
    trade_name: str | None = Field(None, min_length=3, max_length=150)
    cnpj: str | None = Field(None, min_length=5, max_length=14)


class TenderCreateSchema(BaseModel):
    tender_number: int
    tender_year: int
    object_description: str
    public_body_name: str
    modality: TenderModality
    format: TenderFormat
    session_date: datetime


class TenderUpdateSchema(BaseModel):
    tender_number: int | None = None
    tender_year: int | None = None
    object_description: str | None = None
    public_body_name: str | None = None
    modality: TenderModality | None = None
    format: TenderFormat | None = None
    session_date: datetime | None = None
    status: TenderStatus | None = None
    participation_result: ParticipationResult | None = None
    awarded_value: Decimal | None = None


class TenderPublicSchema(BaseModel):
    id: int
    tender_number: int
    tender_year: int
    object_description: str
    public_body_name: str
    modality: TenderModality
    format: TenderFormat
    status: TenderStatus
    participation_result: ParticipationResult | None
    awarded_value: str | None
    session_date: datetime
    created_at: datetime
