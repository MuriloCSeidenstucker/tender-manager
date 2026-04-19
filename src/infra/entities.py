# pylint: disable=E1102:not-callable

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


@mapped_as_dataclass(table_registry)
class UserEntity:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    companies: Mapped[list["CompanyEntity"]] = relationship(
        init=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )


@mapped_as_dataclass(table_registry)
class CompanyEntity:
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    trade_name: Mapped[str]
    cnpj: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    tenders: Mapped[list["TenderEntity"]] = relationship(
        init=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class TenderModality(str, Enum):
    PUBLIC_TENDER = "public_tender"  # Concorrência
    PRICE_QUOTATION = "price_quotation"  # Tomada de Preços
    INVITATION = "invitation"  # Convite
    AUCTION = "auction"  # Leilão
    CONTEST = "contest"  # Concurso
    TRADING_SESSION = "trading_session"  # Pregão
    DIRECT_CONTRACTING = "direct_contracting"  # Dispensa/Inexigibilidade


class TenderFormat(str, Enum):
    ELECTRONIC = "electronic"  # Eletrônico
    IN_PERSON = "in_person"  # Presencial


class TenderStatus(str, Enum):
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    APPROVED = "approved"
    REJECTED = "rejected"
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    APPEAL = "appeal"
    FINISHED = "finished"
    SUSPENDED = "suspended"
    CANCELED = "canceled"


class ParticipationResult(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


@mapped_as_dataclass(table_registry)
class TenderEntity:
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    tender_number: Mapped[int]
    tender_year: Mapped[int]
    object_description: Mapped[str]
    public_body_name: Mapped[str]
    modality: Mapped[TenderModality]
    format: Mapped[TenderFormat]
    status: Mapped[TenderStatus]
    participation_result: Mapped[ParticipationResult | None] = mapped_column(
        nullable=True
    )
    awarded_value: Mapped[Decimal | None] = mapped_column(nullable=True)
    session_date: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
