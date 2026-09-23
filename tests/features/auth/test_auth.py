from httpx import AsyncClient


async def test_register_then_login(client: AsyncClient) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"name": "Ada Lovelace", "email": "ada@example.com", "password": "supersecret123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "ada@example.com"

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "supersecret123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


async def test_login_with_wrong_password_is_rejected(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Grace Hopper", "email": "grace@example.com", "password": "supersecret123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "grace@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_get_my_profile_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
