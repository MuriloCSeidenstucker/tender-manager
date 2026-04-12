from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=6, max_length=128)


class UserPublicSchema(UserBaseSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None


class UserPasswordUpdateSchema(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]
