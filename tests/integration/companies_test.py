from http import HTTPStatus

import pytest

from tests.factories import CompanyFactory


async def test_create_company(client, token):
    response = await client.post(
        "/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test create company",
            "trade_name": "Test create company trade_name",
            "cnpj": "12345678901234",
        },
    )
    assert response.json() == {
        "id": 1,
        "name": "Test create company",
        "trade_name": "Test create company trade_name",
        "cnpj": "12345678901234",
    }


async def test_create_company_invalid_name(client, token):
    response = await client.post(
        "/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "ab",
            "trade_name": "valid trade name",
            "cnpj": "12345678901234",
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_create_company_invalid_trade_name(client, token):
    response = await client.post(
        "/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "valid name",
            "trade_name": "ab",
            "cnpj": "12345678901234",
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_create_company_invalid_cnpj(client, token):
    response = await client.post(
        "/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "valid name",
            "trade_name": "valid trade name",
            "cnpj": "123",
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_list_companies_invalid_filter_name(client, token):
    response = await client.get(
        "/companies/?name=ab",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_companies_should_return_5_companies(session, client, user, token):
    expected_companies = 5
    session.add_all(CompanyFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        "/companies/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


@pytest.mark.asyncio
async def test_list_companies_pagination_should_return_2_companies(
    session, user, client, token
):
    expected_companies = 2
    session.add_all(CompanyFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        "/companies/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


@pytest.mark.asyncio
async def test_list_companies_filter_name_should_return_5_companies(
    session, user, client, token
):
    expected_companies = 5
    session.add_all(
        CompanyFactory.create_batch(5, user_id=user.id, name="Test company 1")
    )
    await session.commit()

    response = await client.get(
        "/companies/?name=Test company 1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


@pytest.mark.asyncio
async def test_list_companies_filter_trade_name_should_return_5_companies(
    session, user, client, token
):
    expected_companies = 5
    session.add_all(
        CompanyFactory.create_batch(5, user_id=user.id, trade_name="trade name")
    )
    await session.commit()

    response = await client.get(
        "/companies/?trade_name=trade name",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


@pytest.mark.asyncio
async def test_list_companies_filter_cnpj_should_return_5_companies(
    session, user, client, token
):
    expected_companies = 5
    session.add_all(
        CompanyFactory.create_batch(5, user_id=user.id, cnpj="12345678901234")
    )
    await session.commit()

    response = await client.get(
        "/companies/?cnpj=12345678901234",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


@pytest.mark.asyncio
async def test_list_companies_filter_combined_should_return_5_companies(
    session, user, client, token
):
    expected_companies = 5
    session.add_all(
        CompanyFactory.create_batch(
            5,
            user_id=user.id,
            name="Test company combined",
            trade_name="combined trade name",
            cnpj="12345678901234",
        )
    )

    session.add_all(
        CompanyFactory.create_batch(
            3,
            user_id=user.id,
            name="Other name",
            trade_name="other trade name",
            cnpj="00000000000000",
        )
    )
    await session.commit()

    response = await client.get(
        "/companies/?name=Test company combined&trade_name=combined trade name&cnpj=12345678901234",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


@pytest.mark.asyncio
async def test_patch_company(session, client, user, token):
    company = CompanyFactory(user_id=user.id)

    session.add(company)
    await session.commit()

    response = await client.patch(
        f"/companies/{company.id}",
        json={"name": "teste name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "teste name"


async def test_patch_company_error(client, token):
    response = await client.patch(
        "/companies/10",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Company not found."}


@pytest.mark.asyncio
async def test_patch_company_invalid_name(session, client, user, token):
    company = CompanyFactory(user_id=user.id)
    session.add(company)
    await session.commit()

    response = await client.patch(
        f"/companies/{company.id}",
        json={"name": "ab"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_company(session, client, user, token):
    company = CompanyFactory(user_id=user.id)

    session.add(company)
    await session.commit()

    response = await client.delete(
        f"/companies/{company.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Company has been deleted successfully."}


async def test_delete_company_error(client, token):
    response = await client.delete(
        f"/companies/{10}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Company not found."}
