from uuid import uuid4
from typing import Tuple

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from fastapi import FastAPI, Request


def prepare_mongo_db(connection_string: str, db_name: str) -> Tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    client = AsyncIOMotorClient(connection_string)
    db = client[db_name]
    return client, db


def gen_id():
    return uuid4().hex[:16]


# TASKS
def set_task_collection(app: FastAPI, mongodb: AsyncIOMotorDatabase) -> None:
    app.task_collection = mongodb.tasks


def get_task_collection(request: Request) -> AsyncIOMotorCollection:
    return request.app.task_collection


# USERS
def set_user_collection(app: FastAPI, mongodb: AsyncIOMotorDatabase) -> None:
    app.user_collection = mongodb.users


def get_user_collection(request: Request) -> AsyncIOMotorCollection:
    return request.app.user_collection
