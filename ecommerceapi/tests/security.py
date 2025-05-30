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
