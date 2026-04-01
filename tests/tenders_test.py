from http import HTTPStatus

import pytest

from src.infra.entities import TenderEntity
from tests.factories import CompanyFactory, TenderFactory


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


@pytest.mark.asyncio
async def test_list_tenders_should_return_tenders(session, client, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tenders = TenderFactory.create_batch(5, company_id=company.id)
    session.add_all(tenders)
    await session.commit()

    response = client.get(
        f"/companies/{company.id}/tenders/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["tenders"]) == 5


@pytest.mark.asyncio
async def test_list_tenders_should_return_only_company_tenders(
    session, client, user, token
):
    company1 = CompanyFactory(user_id=user.id)
    company2 = CompanyFactory(user_id=user.id)

    session.add_all([company1, company2])
    await session.commit()
    await session.refresh(company1)
    await session.refresh(company2)

    session.add_all(TenderFactory.create_batch(3, company_id=company1.id))
    session.add_all(TenderFactory.create_batch(2, company_id=company2.id))
    await session.commit()

    response = client.get(
        f"/companies/{company1.id}/tenders/",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    assert len(data["tenders"]) == 3


@pytest.mark.asyncio
async def test_list_tenders_should_return_404_when_company_not_found(client, token):
    response = client.get(
        "/companies/999/tenders/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tenders_should_not_access_other_user_company(
    session, client, other_user, token
):
    company = CompanyFactory(user_id=other_user.id)
    session.add(company)
    await session.commit()

    response = client.get(
        f"/companies/{company.id}/tenders/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_tender_success(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()
    await session.refresh(tender)

    payload = {
        "object_description": "Updated description",
        "status": "approved",
    }

    response = client.patch(
        f"/companies/{company.id}/tenders/{tender.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["object_description"] == "Updated description"
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_patch_tender_not_found(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    response = client.patch(
        f"/companies/{company.id}/tenders/9999",
        json={"status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Tender not found."


@pytest.mark.asyncio
async def test_patch_tender_company_not_owned(client, session, other_user, token):
    company = CompanyFactory(user_id=other_user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()

    response = client.patch(
        f"/companies/{company.id}/tenders/{tender.id}",
        json={"status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_patch_tender_partial_update_only(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tender = TenderFactory(
        company_id=company.id,
        object_description="Original",
    )
    session.add(tender)
    await session.commit()
    await session.refresh(tender)

    payload = {"status": "approved"}

    response = client.patch(
        f"/companies/{company.id}/tenders/{tender.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK

    db_tender = await session.get(TenderEntity, tender.id)

    assert db_tender.status.value == "approved"
    assert db_tender.object_description == "Original"


@pytest.mark.asyncio
async def test_patch_tender_multiple_fields(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()
    await session.refresh(tender)

    payload = {
        "tender_number": 999,
        "tender_year": 2030,
        "status": "finished",
        "format": "electronic",
    }

    response = client.patch(
        f"/companies/{company.id}/tenders/{tender.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK

    db_tender = await session.get(TenderEntity, tender.id)

    assert db_tender.tender_number == 999
    assert db_tender.tender_year == 2030
    assert db_tender.status.value == "finished"
    assert db_tender.format.value == "electronic"


@pytest.mark.asyncio
async def test_delete_tender_success(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()
    await session.refresh(tender)

    response = client.delete(
        f"/companies/{company.id}/tenders/{tender.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Tender has been deleted successfully."}

    db_tender = await session.get(TenderEntity, tender.id)
    assert db_tender is None


@pytest.mark.asyncio
async def test_delete_tender_not_found(client, session, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    response = client.delete(
        f"/companies/{company.id}/tenders/9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Tender not found."


@pytest.mark.asyncio
async def test_delete_tender_company_not_owned(client, session, other_user, token):
    company = CompanyFactory(user_id=other_user.id)
    session.add(company)
    await session.commit()
    await session.refresh(company)

    tender = TenderFactory(company_id=company.id)
    session.add(tender)
    await session.commit()

    response = client.delete(
        f"/companies/{company.id}/tenders/{tender.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_delete_tender_wrong_company(client, session, user, token):
    company1 = CompanyFactory(user_id=user.id)
    session.add(company1)

    company2 = CompanyFactory(user_id=user.id)
    session.add(company2)

    await session.commit()

    tender = TenderFactory(company_id=company1.id)
    session.add(tender)
    await session.commit()

    response = client.delete(
        f"/companies/{company2.id}/tenders/{tender.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Tender not found."
