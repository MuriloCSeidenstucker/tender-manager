from http import HTTPStatus

import factory
import pytest

from src.infra.entities import CompanyEntity


class CompanyFactory(factory.Factory):
    class Meta:
        model = CompanyEntity

    name = factory.Faker("text")
    trade_name = factory.Faker("text")
    cnpj = factory.Faker("text")
    user_id = 1


def test_create_company(client, token):
    response = client.post(
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


@pytest.mark.asyncio
async def test_list_companies_should_return_5_companies(session, client, user, token):
    expected_companies = 5
    session.add_all(CompanyFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
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

    response = client.get(
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

    response = client.get(
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

    response = client.get(
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

    response = client.get(
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

    response = client.get(
        "/companies/?name=Test company combined&trade_name=combined trade name&cnpj=12345678901234",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["companies"]) == expected_companies


def test_patch_company_error(client, token):
    response = client.patch(
        "/companies/10",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Company not found."}


@pytest.mark.asyncio
async def test_patch_company(session, client, user, token):
    company = CompanyFactory(user_id=user.id)

    session.add(company)
    await session.commit()

    response = client.patch(
        f"/companies/{company.id}",
        json={"name": "teste name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "teste name"


@pytest.mark.asyncio
async def test_delete_company(session, client, user, token):
    company = CompanyFactory(user_id=user.id)

    session.add(company)
    await session.commit()

    response = client.delete(
        f"/companies/{company.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Company has been deleted successfully."}


def test_delete_company_error(client, token):
    response = client.delete(
        f"/companies/{10}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Company not found."}
