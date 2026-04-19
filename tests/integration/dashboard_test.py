# pylint: disable=W0613:unused-argument

from datetime import datetime
from decimal import Decimal
from http import HTTPStatus

import pytest

from src.infra.entities import ParticipationResult
from tests.factories import CompanyFactory, TenderFactory


@pytest.mark.asyncio
async def test_dashboard_metrics_empty(client, user, token):
    year = datetime.now().year
    response = client.get(
        "/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"},
        params={"year": year},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["year"] == year
    assert data["companies"] == []


@pytest.mark.asyncio
async def test_dashboard_metrics_company_no_tenders(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    year = datetime.now().year
    response = client.get(
        "/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"},
        params={"year": year},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data["companies"]) == 1
    company_data = data["companies"][0]
    assert company_data["total_tenders"] == 0
    assert company_data["won_tenders"] == 0
    assert Decimal(company_data["total_awarded_value"]) == Decimal("0")


@pytest.mark.asyncio
async def test_dashboard_metrics_with_tenders(client, session, user, token):
    year = datetime.now().year
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    won_tender = TenderFactory(
        company_id=company.id,
        tender_year=year,
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("5000.00"),
    )
    lost_tender = TenderFactory(
        company_id=company.id,
        tender_year=year,
        participation_result=ParticipationResult.LOST,
        awarded_value=None,
    )
    session.add_all([won_tender, lost_tender])
    await session.commit()

    response = client.get(
        "/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"},
        params={"year": year},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    company_data = data["companies"][0]
    assert company_data["total_tenders"] == 2
    assert company_data["won_tenders"] == 1
    assert Decimal(company_data["total_awarded_value"]) == Decimal("5000.00")


@pytest.mark.asyncio
async def test_dashboard_metrics_filters_by_year(client, session, user, token):
    current_year = datetime.now().year
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    current_year_tender = TenderFactory(
        company_id=company.id,
        tender_year=current_year,
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("1000.00"),
    )
    old_year_tender = TenderFactory(
        company_id=company.id,
        tender_year=current_year - 1,
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("9999.00"),
    )
    session.add_all([current_year_tender, old_year_tender])
    await session.commit()

    response = client.get(
        "/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"},
        params={"year": current_year},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    company_data = data["companies"][0]
    assert company_data["total_tenders"] == 1
    assert Decimal(company_data["total_awarded_value"]) == Decimal("1000.00")


@pytest.mark.asyncio
async def test_dashboard_metrics_isolates_user_companies(
    client, session, user, other_user, token
):
    my_company = CompanyFactory(user_id=user.id)
    other_company = CompanyFactory(user_id=other_user.id)
    session.add_all([my_company, other_company])
    await session.commit()

    response = client.get(
        "/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    company_ids = [c["company_id"] for c in data["companies"]]
    assert my_company.id in company_ids
    assert other_company.id not in company_ids


def test_dashboard_metrics_requires_auth(client):
    response = client.get("/dashboard/metrics")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
