import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

os.environ["ENV_STATE"] = "test"

from ecommerceapi.database import database, user_table  # noqa: 402
from ecommerceapi.main import app  # noqa: 402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# crear un cliente sincrono
@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


# crea un cliente asincrono
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac

@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "password"}
    await async_client.post(
        "/register", json=user_details
    )
    query = user_table.select().where(user_table.c.email == user_details["email"])
    response = await database.fetch_one(query)
    user_details["id"] = response["id"]
    return user_details