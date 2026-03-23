from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class CompanySchema(BaseModel):
    name: str
    trade_name: str
    cnpj: str


class CompanyPublicSchema(CompanySchema):
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
