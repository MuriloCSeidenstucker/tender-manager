from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.infra.entities import (
    ParticipationResult,
    TenderFormat,
    TenderModality,
    TenderStatus,
)
from src.schemas.common import FilterPageSchema

BR_TZ = ZoneInfo("America/Sao_Paulo")


class TenderBaseSchema(BaseModel):
    tender_number: int = Field(..., gt=0)
    tender_year: int = Field(..., ge=2000, le=2100)
    object_description: str = Field(..., min_length=3, max_length=500)
    public_body_name: str = Field(..., min_length=3, max_length=150)
    modality: TenderModality
    format: TenderFormat
    session_date: datetime | None = None


class TenderCreateSchema(TenderBaseSchema):
    status: TenderStatus | None = None

    # Regra: ParticipationResult padrão como PENDING
    participation_result: ParticipationResult = ParticipationResult.PENDING

    # Regra: Data atual no fuso de brasília se omitida
    session_date: datetime | None = Field(default_factory=lambda: datetime.now(BR_TZ))
    awarded_value: Decimal | None = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_business_rules(self):
        # Regra: Se marcou como LOST, awarded_value deve ser 0
        if self.participation_result == ParticipationResult.LOST:
            self.awarded_value = Decimal("0.0")

        # Regra: awarded_value > 0 depende do status
        if self.awarded_value is not None and self.awarded_value > 0:
            blocked_statuses = {
                TenderStatus.MONITORING,
                TenderStatus.ANALYSIS,
                TenderStatus.APPROVED,
                TenderStatus.REJECTED,
                TenderStatus.REGISTERED,
                TenderStatus.SUSPENDED,
                TenderStatus.CANCELED,
            }
            if self.status in blocked_statuses:
                raise ValueError(
                    f"O valor não pode ser maior que 0 para o status {self.status.value}"
                )

        return self


class TenderUpdateSchema(BaseModel):
    tender_number: int | None = Field(None, gt=0)
    tender_year: int | None = Field(None, ge=2000, le=2100)

    # Correção de Bug: min_length deve ser 3 (anteriormente estava 10)
    object_description: str | None = Field(None, min_length=3, max_length=500)

    public_body_name: str | None = Field(None, min_length=3, max_length=150)
    modality: TenderModality | None = None
    format: TenderFormat | None = None
    session_date: datetime | None = None
    status: TenderStatus | None = None
    participation_result: ParticipationResult | None = None
    awarded_value: Decimal | None = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_business_rules(self):
        # Validações tolerantes a PATCH (ignora se participation_result ou status não vierem no payload)
        if self.participation_result == ParticipationResult.LOST:
            self.awarded_value = Decimal("0.0")

        if self.awarded_value is not None and self.awarded_value > 0:
            blocked_statuses = {
                TenderStatus.MONITORING,
                TenderStatus.ANALYSIS,
                TenderStatus.APPROVED,
                TenderStatus.REJECTED,
                TenderStatus.REGISTERED,
                TenderStatus.SUSPENDED,
                TenderStatus.CANCELED,
            }
            # Checa o status apenas se ele estiver sendo atualizado no mesmo request
            if self.status and self.status in blocked_statuses:
                raise ValueError(
                    f"O valor não pode ser maior que 0 para o status {self.status.value}"
                )

        return self


class TenderPublicSchema(TenderBaseSchema):
    id: int
    status: TenderStatus
    participation_result: ParticipationResult | None
    awarded_value: Decimal | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenderListSchema(BaseModel):
    tenders: list[TenderPublicSchema]


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
