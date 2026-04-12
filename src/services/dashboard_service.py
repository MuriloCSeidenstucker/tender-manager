# pylint: disable=E1102:not-callable

from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import CompanyEntity, ParticipationResult, TenderEntity


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_metrics(self, user_id: int, year: int):
        stmt = (
            select(
                CompanyEntity.id.label("company_id"),
                CompanyEntity.name.label("company_name"),
                func.count(TenderEntity.id).label("total_tenders"),
                func.sum(
                    case(
                        (
                            TenderEntity.participation_result
                            == ParticipationResult.WON,
                            1,
                        ),
                        else_=0,
                    )
                ).label("won_tenders"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TenderEntity.participation_result
                                == ParticipationResult.WON,
                                TenderEntity.awarded_value,
                            ),
                            else_=Decimal("0.0"),
                        )
                    ),
                    Decimal("0.0"),
                ).label("total_awarded_value"),
            )
            .outerjoin(
                TenderEntity,
                (TenderEntity.company_id == CompanyEntity.id)
                & (TenderEntity.tender_year == year),
            )
            .where(CompanyEntity.user_id == user_id)
            .group_by(CompanyEntity.id, CompanyEntity.name)
        )

        results = await self.session.execute(stmt)
        companies_data = []

        for row in results:
            companies_data.append(
                {
                    "company_id": row.company_id,
                    "company_name": row.company_name,
                    "total_tenders": row.total_tenders or 0,
                    "won_tenders": row.won_tenders or 0,
                    "total_awarded_value": Decimal(row.total_awarded_value),
                }
            )

        return {"year": year, "companies": companies_data}
