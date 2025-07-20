import pytest

from ecommerceapi import security


@pytest.mark.anyio
async def test_get_user(registered_user):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("sample@sample.com")
    assert user is None


@pytest.mark.anyio
async def test_get_password_hash(registered_user):
    hashed_password = security.get_password_hash(registered_user["password"])
    assert hashed_password != registered_user["password"]
    assert security.verify_password(registered_user["password"], hashed_password)


@pytest.mark.anyio
async def test_get_current_user(registered_user):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalid_token")
