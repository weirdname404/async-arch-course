import logging
from datetime import timedelta

from common.helpers import get_user_collection_from_req
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorCollection

from .. import config
from ..models.auth_models import Token
from ..models.user_models import UserModel, UserModelOut
from ..security import create_access_token, verify_password
from . import auth

logger = logging.getLogger('uvicorn')
router = APIRouter()


async def authenticate_user(username: str, plain_password: str, users: AsyncIOMotorCollection) -> UserModel | bool:
    logger.info("Authenticating user")
    user = await users.find_one({"username": username})
    if user is None:
        return False
    user = UserModel(**user)
    if not verify_password(plain_password, user.password):
        return False
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    user = await authenticate_user(form_data.username, form_data.password, users)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("Giving token")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINS)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", response_model=UserModelOut)
async def get_current_user_data(current_active_user: UserModel = Depends(auth.get_current_active_user)):
    return current_active_user
