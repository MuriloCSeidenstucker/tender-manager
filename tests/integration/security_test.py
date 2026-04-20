from http import HTTPStatus

from jwt import decode

from src.security import create_access_token, settings


async def test_security_create_access_token_returns_valid_jwt():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


async def test_security_access_with_invalid_token_returns_unauthorized(client):
    response = await client.delete(
        "/users/1", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
