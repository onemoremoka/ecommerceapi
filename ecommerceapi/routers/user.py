import logging

from fastapi import APIRouter, HTTPException, status

from ecommerceapi.database import database, user_table
from ecommerceapi.models.user import UserIn
from ecommerceapi.security import authenticate_user, create_access_token, get_password_hash, get_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)  # safe password hashing
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    return {"email": user.email, "detail": "User created successfully"}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}
