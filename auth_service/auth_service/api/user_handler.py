from typing import List

from common.constants import UserRole
from common.helpers import get_user_collection_from_req
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from ..models.user_models import CreateUserModel, UpdateUserModel, UserModel, UserModelOut
from ..security import create_user_safely, update_user_safely
from . import auth

router = APIRouter()


@router.patch("/{pub_id}", response_model=UserModelOut)
async def update_user_data(
    pub_id: str,
    update_params: UpdateUserModel,
    current_active_user: UserModel = Depends(auth.get_current_active_user),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    sensetive_params = update_params.role is not None or update_params.is_active is not None
    if sensetive_params and current_active_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=400, detail="Insufficient rights")

    await update_user_safely(users, update_params, pub_id)

    if (user := await users.find_one({'pub_id': pub_id})) is not None:
        return user

    raise HTTPException(status_code=404)


@router.post("/", response_model=UserModelOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    create_params: CreateUserModel,
    _: UserModel = Depends(auth.get_current_active_admin),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    insert_res, _ = await create_user_safely(users, create_params)
    return await users.find_one({'_id': insert_res.inserted_id})


@router.get("/", response_model=List[UserModelOut])
async def list_users(
    _: UserModel = Depends(auth.get_current_active_user),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    return await users.find().to_list(1000)


@router.get("/{pub_id}", response_model=UserModelOut)
async def get_user(
    pub_id: str,
    _: UserModel = Depends(auth.get_current_active_user),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    if (user := await users.find_one({'pub_id': pub_id})) is not None:
        return user

    raise HTTPException(status_code=404)
