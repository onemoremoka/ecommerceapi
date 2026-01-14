import pytest
from fastapi import Request
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
async def test_confirmation_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "example@example.com", "password")
    confirmation_url = str(spy.spy_return)
    response = await async_client.get(confirmation_url)

    assert response.status_code == 200
    assert "User email confirmed successfully" in response.json()["detail"]


@pytest.mark.anyio
async def test_confirmation_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/confirm/invalid_token")
    assert response.status_code == 401
    assert (
        "Token has expired" in response.json()["detail"]
        or "Invalid Token" in response.json()["detail"]
    )


@pytest.mark.anyio
async def test_confirmation_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("ecommerceapi.security.confirm_token_expire_minutes", return_value=-1)
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "example@example.com", "password")
    confirmation_url = str(spy.spy_return)
    response = await async_client.get(confirmation_url)

    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post(
        "token",
        json={"email": confirmed_user["email"], "password": confirmed_user["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_user_not_confirmed(
    async_client: AsyncClient, registered_user: dict
):
    response = await async_client.post(
        "token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 401
    assert "User has not confirmed email" in response.json()["detail"]


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
