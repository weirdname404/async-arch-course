from typing import List

from common.helpers import get_task_collection, get_user_collection
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from motor.motor_asyncio import AsyncIOMotorCollection

from .models import CreateTaskModel, TaskModel, UpdateTaskModel

router = APIRouter()


@router.post('/', summary='Create task', response_model=TaskModel, status_code=status.HTTP_201_CREATED)
async def create_task(task: CreateTaskModel, tasks: AsyncIOMotorCollection = Depends(get_task_collection)):
    task = jsonable_encoder(TaskModel(**task.dict()))
    new_task = await tasks.insert_one(task)
    created_task = await tasks.find_one({'_id': new_task.inserted_id})
    return created_task


@router.get('/{task_id}', summary='Get specific task', response_model=TaskModel)
async def get_task(task_id: str, tasks: AsyncIOMotorCollection = Depends(get_task_collection)):
    if (task := await tasks.find_one({'pub_id': task_id})) is not None:
        return task

    raise HTTPException(status_code=404)


@router.get('/', summary='Get all tasks', response_model=List[TaskModel])
async def list_tasks(tasks: AsyncIOMotorCollection = Depends(get_task_collection)):
    return await tasks.find().to_list(1000)


@router.get('/shuffle/', summary='Shuffle all tasks', response_model=List[TaskModel])
async def shuffle_tasks(tasks: AsyncIOMotorCollection = Depends(get_task_collection)):
    # TODO add shuffle logic
    return await tasks.find().to_list(1000)


@router.patch('/{task_id}', summary='Update task', response_model=TaskModel)
async def update_task(
    update_data: UpdateTaskModel, task_id: str, tasks: AsyncIOMotorCollection = Depends(get_task_collection)
):
    update_dict = update_data.dict(exclude_unset=True)
    if update_dict:
        await tasks.update_one({"pub_id": task_id}, {"$set": update_dict})

    if (task := await tasks.find_one({'pub_id': task_id})) is not None:
        return task

    raise HTTPException(status_code=404)


@router.delete('/{task_id}', summary='Delete specific task', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, tasks: AsyncIOMotorCollection = Depends(get_task_collection)):
    delete_result = await tasks.delete_one({'pub_id': task_id})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404)
