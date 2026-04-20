# pylint: disable=W0613:unused-argument

from http import HTTPStatus

from freezegun import freeze_time


async def test_auth_login_with_valid_credentials_returns_token(client, user):
    response = await client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token
    assert "token_type" in token


async def test_auth_expired_token_returns_unauthorized(client, user):
    with freeze_time("2023-07-14 12:00:00"):
        response = await client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 12:31:00"):
        response = await client.patch(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


async def test_auth_login_with_inexistent_user_returns_unauthorized(client):
    response = await client.post(
        "/auth/token",
        data={"username": "no_user@no_domain.com", "password": "testtest"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_auth_login_with_wrong_password_returns_unauthorized(client, user):
    response = await client.post(
        "/auth/token", data={"username": user.email, "password": "wrong_password"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_auth_refresh_token_with_valid_token_returns_new_token(
    client, user, token
):
    response = await client.post(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


async def test_auth_refresh_token_with_expired_token_returns_unauthorized(client, user):
    with freeze_time("2023-07-14 12:00:00"):
        response = await client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 12:31:00"):
        response = await client.post(
            "/auth/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}
