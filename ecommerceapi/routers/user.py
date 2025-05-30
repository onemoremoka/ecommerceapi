from fastapi import APIRouter, status, HTTPException
from ecommerceapi.models.user import UserIn
from ecommerceapi.security import get_user
from ecommerceapi.database import user_table, database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    query = user_table.insert().values(
        email=user.email,
        password=user.password
    )
    logger.debug(query)
    await database.execute(query)
    return {"email": user.email}