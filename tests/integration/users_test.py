from http import HTTPStatus

from src.schemas.user import UserPublicSchema


async def test_user_create_with_valid_payload_returns_created(client):
    response = await client.post(
        "/users/",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "alice",
        "email": "alice@example.com",
        "id": 1,
    }


async def test_user_list_returns_authenticated_user(client, user, token):
    user_schema = UserPublicSchema.model_validate(user).model_dump()
    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


async def test_user_list_when_users_exist_returns_user_list(client, user, token):
    user_schema = UserPublicSchema.model_validate(user).model_dump()
    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"users": [user_schema]}


async def test_user_list_unauthorized_returns_unauthorized(client):
    response = await client.get("/users/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


async def test_user_update_with_valid_payload_returns_ok(client, user, token):
    response = await client.patch(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": 1,
    }


async def test_user_update_with_existing_identity_returns_conflict(client, user, token):
    await client.post(
        "/users/",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response_update = await client.patch(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "bob@example.com",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": "Username or Email already exists"}


async def test_user_update_another_user_returns_forbidden(client, other_user, token):
    response = await client.patch(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


async def test_user_update_password_with_valid_credentials_returns_ok(
    client, user, token
):
    response = await client.patch(
        f"/users/{user.id}/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": user.clean_password,
            "new_password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Password updated successfully"}


async def test_user_update_password_with_wrong_current_password_returns_unprocessable(
    client, user, token
):
    response = await client.patch(
        f"/users/{user.id}/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {"detail": "Invalid current password"}


async def test_user_delete_with_authorized_user_returns_ok(client, user, token):
    response = await client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


async def test_user_delete_another_user_returns_forbidden(client, other_user, token):
    response = await client.delete(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}
