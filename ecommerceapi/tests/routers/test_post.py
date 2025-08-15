import pytest
from httpx import AsyncClient
from ecommerceapi import security

# funciones auxiliares
async def create_post(body: str, async_client: AsyncClient, logged_with_token: str) -> dict:
    response = await async_client.post("/post", json={"body": body}, headers={"Authorization": f"Bearer {logged_with_token}"})
    return response.json()


async def create_comment(body: str, post_id: int, async_client: int, logged_with_token: str) -> dict:
    response = await async_client.post(
        "/comment", json={"body": body, "post_id": post_id}, headers={"Authorization": f"Bearer {logged_with_token}"}
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_with_token: str) -> dict:
    return await create_post("body request", async_client, logged_with_token)


@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict, logged_with_token: str):
    return await create_comment("Test Comment", created_post["id"], async_client, logged_with_token)

# -----------------------------------------------------------

@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient, registered_user: dict, logged_with_token: str):
    body = "test body"

    response = await async_client.post("/post", json={"body": body}, headers={"Authorization": f"Bearer {logged_with_token}"})

    assert response.status_code == 201
    assert {"id": 1, "body": body, "user_id": registered_user["id"]}.items() <= response.json().items()

@pytest.mark.anyio
async def test_create_post_expired_token(async_client: AsyncClient, registered_user: dict, mocker):
    mocker.patch("ecommerceapi.security.access_token_expire_minutes", return_value=-1)  # Set token to expire immediately
    token = security.create_access_token(registered_user["email"])
    response = await async_client.post("/post", json={"body": "test body"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient, logged_with_token: str):
    response = await async_client.post("/post", json={}, headers={"Authorization": f"Bearer {logged_with_token}"})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")

    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    assert response.status_code == 200
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")

    assert response.status_code == 200
    assert response.json() == {"post": created_post, "comments": [created_comment]}


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/2")
    assert response.status_code == 404
