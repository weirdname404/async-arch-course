from datetime import datetime, timedelta
from typing import Tuple

from fastapi.encoders import jsonable_encoder
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.context import CryptContext

from . import config
from .models.user_models import CreateUserModel, UpdateUserModel, UserModel

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt


async def create_user_safely(users: AsyncIOMotorCollection, create_params: CreateUserModel) -> Tuple[dict, UserModel]:
    user = UserModel(**create_params.dict())
    user.password = get_password_hash(user.password)
    return await users.insert_one(jsonable_encoder(user)), user


async def update_user_safely(
    users: AsyncIOMotorCollection, update_params: UpdateUserModel, user_id: str
) -> dict | None:
    if update_params.password:
        update_params.password = get_password_hash(update_params.password)
    update_dict = update_params.dict(exclude_unset=True)
    if update_dict:
        return await users.update_one({"pub_id": user_id}, {"$set": update_dict})
