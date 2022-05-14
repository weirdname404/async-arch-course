from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from .constants import UserRole
from .helpers import get_user_collection_from_req

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_username_from_token(token: str, secret_key: str, algorithm: str) -> str:
    try:
        payload = jwt.decode(token, secret_key, algorithm)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


class Auth(BaseModel):
    get_current_active_user: Callable
    get_current_active_admin: Callable


def auth_user_factory(
    oauth2_scheme: OAuth2PasswordBearer,
    secret_key: str,
    algorithm: str,
    user_model: BaseModel,
) -> Auth:
    """Factory produces class with methods that authenticate user and check rights"""

    async def get_current_user(
        users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
        token: str = Depends(oauth2_scheme),
    ):
        username = get_username_from_token(token, secret_key, algorithm)
        user = await users.find_one({"username": username})
        if user is None:
            raise credentials_exception
        return user_model(**user)

    async def get_current_active_user(
        current_user: user_model | None = Depends(get_current_user),
    ) -> user_model | None:
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    async def get_current_active_admin(
        current_user: user_model | None = Depends(get_current_active_user),
    ) -> user_model | None:
        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(status_code=400, detail="Insufficient rights")
        return current_user

    return Auth(
        get_current_active_user=get_current_active_user,
        get_current_active_admin=get_current_active_admin,
    )
