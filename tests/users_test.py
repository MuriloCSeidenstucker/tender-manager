from http import HTTPStatus

from src.schemas.user import UserPublicSchema


def test_create_user(client):
    response = client.post(
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


def test_read_users(client):
    response = client.get("/users")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_read_users_with_users(client, user):
    user_schema = UserPublicSchema.model_validate(user).model_dump()
    response = client.get("/users/")
    assert response.json() == {"users": [user_schema]}


def test_update_user(client, user, token):
    response = client.patch(
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


def test_update_integrity_error(client, user, token):
    client.post(
        "/users",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response_update = client.patch(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "bob@example.com",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": "Username or Email already exists"}


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.patch(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


def test_update_password(client, user, token):
    response = client.patch(
        f"/users/{user.id}/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": user.clean_password,
            "new_password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Password updated successfully"}


def test_update_password_wrong_current(client, user, token):
    response = client.patch(
        f"/users/{user.id}/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {"detail": "Invalid current password"}


def test_delete_user(client, user, token):
    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_wrong_user(client, other_user, token):
    response = client.delete(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}
