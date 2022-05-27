from typing import List

from common.auth import auth_user_factory
from common.constants import UserRole
from common.helpers import get_task_collection_from_req, get_user_collection_from_req
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorCollection

from . import config
from .models import CreateTaskModel, TaskModel, TaskModelOut, UpdateTaskModel, UserModel

router = APIRouter()
auth = auth_user_factory(
    oauth2_scheme=OAuth2PasswordBearer(tokenUrl=config.AUTH_URL),
    secret_key=config.SECRET_KEY,
    algorithm=config.ALGORITHM,
    user_model=UserModel,
)


@router.post('/', summary='Create task', response_model=TaskModelOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: CreateTaskModel,
    tasks: AsyncIOMotorCollection = Depends(get_task_collection_from_req),
    users: AsyncIOMotorCollection = Depends(get_user_collection_from_req),
    _: UserModel = Depends(auth.get_current_active_user),
):
    assignee_dict = await users.find_one({'_id': task.assignee_id})
    if not assignee_dict:
        raise HTTPException(status_code=404, detail="User not found")
    assignee = UserModel(**assignee_dict)
    if assignee.role != UserRole.DEV.value:
        raise HTTPException(status_code=400, detail="Task can be assigned only to a developer.")

    task = jsonable_encoder(TaskModel(**task.dict()))
    new_task = await tasks.insert_one(task)
    created_task = await tasks.find_one({'_id': new_task.inserted_id})
    return created_task


@router.get('/{task_id}', summary='Get specific task', response_model=TaskModelOut)
async def get_task(
    task_id: str,
    tasks: AsyncIOMotorCollection = Depends(get_task_collection_from_req),
    _: UserModel = Depends(auth.get_current_active_user),
):
    if (task := await tasks.find_one({'pub_id': task_id})) is not None:
        return task

    raise HTTPException(status_code=404)


@router.get('/', summary='Get all tasks', response_model=List[TaskModelOut])
async def list_tasks(
    tasks: AsyncIOMotorCollection = Depends(get_task_collection_from_req),
    _: UserModel = Depends(auth.get_current_active_user),
):
    # TODO add pagination
    return await tasks.find().to_list(1000)


@router.get('/shuffle/', summary='Shuffle all tasks', response_model=List[TaskModelOut])
async def shuffle_tasks(
    tasks: AsyncIOMotorCollection = Depends(get_task_collection_from_req),
    _: UserModel = Depends(auth.get_current_active_user),
):
    # TODO add shuffle logic
    return await tasks.find().to_list(1000)


@router.patch('/{task_id}', summary='Update task', response_model=TaskModelOut)
async def update_task(
    update_data: UpdateTaskModel,
    task_id: str,
    tasks: AsyncIOMotorCollection = Depends(get_task_collection_from_req),
    _: UserModel = Depends(auth.get_current_active_user),
):
    update_dict = update_data.dict(exclude_unset=True)
    if update_dict:
        await tasks.update_one({"pub_id": task_id}, {"$set": update_dict})

    if (task := await tasks.find_one({'pub_id': task_id})) is not None:
        return task

    raise HTTPException(status_code=404)


@router.delete('/{task_id}', summary='Delete specific task', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    tasks: AsyncIOMotorCollection = Depends(get_task_collection_from_req),
    _: UserModel = Depends(auth.get_current_active_user),
):
    delete_result = await tasks.delete_one({'pub_id': task_id})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404)
