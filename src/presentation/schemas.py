from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.infra.entities import TodoState


class UserSchema(BaseModel):
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


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublicSchema(TodoSchema):
    id: int


class TodoListSchema(BaseModel):
    todos: list[TodoPublicSchema]


class FilterTodoSchema(FilterPageSchema):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    state: TodoState | None = None


class TodoUpdateSchema(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    state: TodoState | None = None
