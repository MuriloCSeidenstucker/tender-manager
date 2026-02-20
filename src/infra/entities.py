# pylint: disable=E1102:not-callable

from datetime import datetime
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


class TodoState(str, Enum):
    DRAFT = "draft"
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    TRASH = "trash"


@mapped_as_dataclass(table_registry)
class UserEntity:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    todos: Mapped[list["TodoEntity"]] = relationship(
        init=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )


@mapped_as_dataclass(table_registry)
class TodoEntity:
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
