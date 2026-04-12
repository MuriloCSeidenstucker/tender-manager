from pydantic import BaseModel, Field

from src.schemas.common import FilterPageSchema


class CompanyBaseSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    trade_name: str = Field(..., min_length=3, max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=14)


class CompanyCreateSchema(CompanyBaseSchema):
    pass


class CompanyUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=150)
    trade_name: str | None = Field(None, min_length=3, max_length=150)
    cnpj: str | None = Field(None, min_length=14, max_length=14)


class CompanyPublicSchema(CompanyBaseSchema):
    id: int
    model_config = {"from_attributes": True}


class CompanyListSchema(BaseModel):
    companies: list[CompanyPublicSchema]


class FilterCompanySchema(FilterPageSchema):
    name: str | None = Field(None, min_length=3, max_length=150)
    trade_name: str | None = Field(None, min_length=3, max_length=150)
    cnpj: str | None = Field(None, min_length=5, max_length=14)
