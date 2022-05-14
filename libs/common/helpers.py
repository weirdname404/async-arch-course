from typing import Tuple
from uuid import uuid4

from fastapi import FastAPI, Request
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)


def prepare_mongo_db(
    connection_string: str, db_name: str
) -> Tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    client = AsyncIOMotorClient(connection_string)
    db = client[db_name]
    return client, db


def gen_hex(short: bool = False) -> str:
    return uuid4().hex[:16] if short else uuid4().hex


def gen_uuid() -> str:
    return str(uuid4())


# TASKS
def set_task_collection(app: FastAPI, mongodb: AsyncIOMotorDatabase) -> None:
    app.state.task_collection = mongodb.tasks


def get_task_collection(app: FastAPI) -> AsyncIOMotorCollection:
    return app.state.task_collection


def get_task_collection_from_req(request: Request) -> AsyncIOMotorCollection:
    return request.app.state.task_collection


# USERS
def set_user_collection(app: FastAPI, mongodb: AsyncIOMotorDatabase) -> None:
    app.state.user_collection = mongodb.users


def get_user_collection(app: FastAPI) -> AsyncIOMotorCollection:
    return app.state.user_collection


def get_user_collection_from_req(request: Request) -> AsyncIOMotorCollection:
    return request.app.state.user_collection
