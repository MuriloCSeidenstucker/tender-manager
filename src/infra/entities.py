# pylint: disable=E1102:not-callable

from datetime import datetime

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
