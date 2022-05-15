from typing import List

from common.constants import UserRole
from common.helpers import get_user_collection_from_req
from fastapi import APIRouter, Depends, HTTPException, Response, status
from motor.motor_asyncio import AsyncIOMotorCollection

from ..kafka import (
    send_user_created_event,
    send_user_deleted_event,
    send_user_role_changed_event,
    send_user_updated_event,
)
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
        if update_dict := update_params.get_public_dict():
            update_dict |= {'pub_id': pub_id}
            await send_user_updated_event(update_dict)
            if update_params.role is not None:
                await send_user_role_changed_event(update_dict)

        return user

    raise HTTPException(status_code=404)


@router.post("/", response_model=UserModelOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    create_params: CreateUserModel,
    _: UserModel = Depends(auth.get_current_active_admin),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    insert_res, user = await create_user_safely(users, create_params)
    await send_user_created_event(user.get_public_dict())
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


@router.delete("/{pub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    pub_id: str,
    _: UserModel = Depends(auth.get_current_active_admin),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
):
    delete_result = await users.delete_one({'pub_id': pub_id})
    if delete_result.deleted_count == 1:
        await send_user_deleted_event({'pub_id': pub_id})
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404)
