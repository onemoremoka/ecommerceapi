import pytest
from jose import jwt

from ecommerceapi import security


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


def test_confirm_token_expire_minutes():
    assert security.confirm_token_expire_minutes() == 1440


def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123", "type": "access"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_confirmation_access_token():
    token = security.create_confirmation_token("123")
    assert {"sub": "123", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_get_subject_from_token_type_valid_confirmation():
    sample_email = "sample@example.com"
    token = security.create_confirmation_token(sample_email)
    assert sample_email == security.get_subject_from_token_type(token, type="confirmation")


def test_get_subject_from_token_type_valid_access():
    sample_email = "sample@example.com"
    token = security.create_access_token(sample_email)
    assert sample_email == security.get_subject_from_token_type(token, type="access")


def test_get_subject_from_token_type_expired(mocker):
    mocker.patch("ecommerceapi.security.access_token_expire_minutes", return_value=-1)
    sample_email = "sample@example.com"
    token = security.create_access_token(sample_email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_from_token_type(token, type="access")
    assert "Token has expired" == exc_info.value.detail


def test_get_subject_from_token_type_invalid_token():
    token = "invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_from_token_type(token, type="access")
    assert "Invalid Token" in exc_info.value.detail

def test_get_subject_for_token_type_missing_sub():
    email = "example@example.com"
    token = security.create_access_token(email)
    decoded_payload = jwt.decode(token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM])
    del decoded_payload["sub"]
    modified_token = jwt.encode(decoded_payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_from_token_type(modified_token, type="access")
    assert "Token is missing 'sub' field" == exc_info.value.detail

def test_get_subject_for_token_type_wrong_type():
    email = "example@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_from_token_type(token, type="confirmation")
    assert "Token has incorrect type, expected: confirmation" == exc_info.value.detail


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


@pytest.mark.anyio
async def test_get_current_user_wrong_type_token(registered_user: str):
    token = security.create_confirmation_token(registered_user["email"])

    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
