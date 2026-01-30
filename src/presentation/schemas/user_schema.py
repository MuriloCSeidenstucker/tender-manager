from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublicSchema]


class Message(BaseModel):
    message: str
