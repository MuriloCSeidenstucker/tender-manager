from http import HTTPStatus


async def test_root(client):
    response = await client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!"}
