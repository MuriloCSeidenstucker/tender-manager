import pytest
from httpx import AsyncClient

from src.app import settings


@pytest.mark.asyncio
async def test_should_allow_configured_cors_origins(client: AsyncClient):
    """Garante que as origens configuradas em settings.CORS_ORIGINS sejam permitidas."""
    allowed_origin = settings.CORS_ORIGINS[0]

    response = await client.options(
        "/",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == allowed_origin
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_should_block_unauthorized_cors_origins(client: AsyncClient):
    """Garante que origens não autorizadas não recebam os cabeçalhos de CORS."""
    unauthorized_origin = "https://evil-attacker.com"

    response = await client.options(
        "/",
        headers={
            "Origin": unauthorized_origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("access-control-allow-origin") is None
