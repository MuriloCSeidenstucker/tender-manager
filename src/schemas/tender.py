from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.infra.entities import (
    ParticipationResult,
    TenderFormat,
    TenderModality,
    TenderStatus,
)
from src.schemas.common import FilterPageSchema


class TenderBaseSchema(BaseModel):
    tender_number: int = Field(..., gt=0)
    tender_year: int = Field(..., ge=2000, le=2100)
    object_description: str = Field(..., min_length=3, max_length=500)
    public_body_name: str = Field(..., min_length=3, max_length=150)
    modality: TenderModality
    format: TenderFormat
    session_date: datetime | None = None


class TenderCreateSchema(TenderBaseSchema):
    status: TenderStatus | None = TenderStatus.MONITORING
    participation_result: ParticipationResult = ParticipationResult.PENDING
    awarded_value: Decimal | None = Field(None, ge=0)


class TenderUpdateSchema(BaseModel):
    tender_number: int | None = Field(None, gt=0)
    tender_year: int | None = Field(None, ge=2000, le=2100)
    object_description: str | None = Field(None, min_length=3, max_length=500)
    public_body_name: str | None = Field(None, min_length=3, max_length=150)
    modality: TenderModality | None = None
    format: TenderFormat | None = None
    session_date: datetime | None = None
    status: TenderStatus | None = None
    participation_result: ParticipationResult | None = None
    awarded_value: Decimal | None = Field(None, ge=0)


class TenderResponse(TenderBaseSchema):
    id: int
    status: TenderStatus
    participation_result: ParticipationResult | None
    awarded_value: Decimal | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenderListSchema(BaseModel):
    tenders: list[TenderResponse]


class FilterTenderSchema(FilterPageSchema):
    tender_number: int | None = None
    tender_year: int | None = None
    object_description: str | None = None
    public_body_name: str | None = None
    modality: TenderModality | None = None
    format: TenderFormat | None = None
    status: TenderStatus | None = None
    participation_result: ParticipationResult | None = None
    session_date: datetime | None = None
