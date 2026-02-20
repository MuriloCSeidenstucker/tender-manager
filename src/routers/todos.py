from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import TodoEntity, UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas import (
    FilterTodoSchema,
    MessageSchema,
    TodoListSchema,
    TodoPublicSchema,
    TodoSchema,
    TodoUpdateSchema,
)
from src.security import get_current_user

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoPublicSchema)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: Session,
):
    db_todo = TodoEntity(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get("/", response_model=TodoListSchema)
async def list_todos(
    session: Session,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodoSchema, Query()],
):
    query = select(TodoEntity).where(TodoEntity.user_id == user.id)

    if todo_filter.title:
        query = query.filter(TodoEntity.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(TodoEntity.description.contains(todo_filter.description))

    if todo_filter.state:
        query = query.filter(TodoEntity.state == todo_filter.state)

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {"todos": todos.all()}


@router.patch("/{todo_id}", response_model=TodoPublicSchema)
async def patch_todo(
    todo_id: int, session: Session, user: CurrentUser, todo: TodoUpdateSchema
):
    db_todo = await session.scalar(
        select(TodoEntity).where(
            TodoEntity.user_id == user.id, TodoEntity.id == todo_id
        )
    )

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found.")

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete("/{todo_id}", response_model=MessageSchema)
async def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    todo = await session.scalar(
        select(TodoEntity).where(
            TodoEntity.user_id == user.id, TodoEntity.id == todo_id
        )
    )

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found.")

    await session.delete(todo)
    await session.commit()

    return {"message": "Task has been deleted successfully."}
