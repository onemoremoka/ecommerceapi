import pytest
from httpx import AsyncClient


# AsyncClient performs HTTP requests in an asynchronous context
# it's not a fixture because we want to use it directly in the test function
async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(
        async_client,
        "example@example.com",
        "password",
    )
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    response = await register_user(
        async_client,
        registered_user["email"],
        registered_user["password"],
    )
    print("asaadsasd", response.json())
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "token",
        json={
            "email": "nonexistent@example.com",
            "password": "xxpassword",
        },
    )
    assert response.status_code == 401
