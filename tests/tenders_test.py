from http import HTTPStatus

import pytest

from tests.factories.company_factory import CompanyFactory


@pytest.mark.asyncio
async def test_create_tender_success(session, client, user, token):
    company = CompanyFactory(user_id=user.id)

    session.add(company)
    await session.commit()

    response = client.post(
        f"/companies/{company.id}/tenders/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tender_number": 123,
            "tender_year": 2025,
            "object_description": "Test tender",
            "public_body_name": "City Hall",
            "modality": "public_tender",
            "format": "electronic",
            "session_date": "2025-01-01T10:00:00",
        },
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert "id" in data
    assert data["tender_number"] == 123
    assert data["status"] == "monitoring"
    assert data["participation_result"] is None
    assert data["awarded_value"] is None


@pytest.mark.asyncio
async def test_create_tender_company_not_owned(session, client, other_user, token):
    company = CompanyFactory(user_id=other_user.id)

    session.add(company)
    await session.commit()

    response = client.post(
        f"/companies/{company.id}/tenders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tender_number": 123,
            "tender_year": 2025,
            "object_description": "Test tender",
            "public_body_name": "City Hall",
            "modality": "public_tender",
            "format": "electronic",
            "session_date": "2025-01-01T10:00:00",
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
