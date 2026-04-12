from decimal import Decimal

from pydantic import BaseModel


class CompanyDashboardSchema(BaseModel):
    company_id: int
    company_name: str
    total_tenders: int
    won_tenders: int
    total_awarded_value: Decimal


class DashboardResponseSchema(BaseModel):
    year: int
    companies: list[CompanyDashboardSchema]
