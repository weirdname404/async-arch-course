import logging

from common.helpers import get_user_collection
from common.kafka import events
from common.kafka.models import Event
from common.kafka.serialization import unpack_data
from common.kafka.topics import KAFKA_USER_BIZ_EVENT_KEY, KAFKA_USER_CUD_EVENT_KEY
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorCollection

from .models import UpdateUserModel, UserModel

logger = logging.getLogger('uvicorn')


async def create_user(users: AsyncIOMotorCollection, user: UserModel) -> dict:
    res = await users.insert_one(jsonable_encoder(user))
    logger.info(f'User {res.inserted_id} created')
    return res


async def handle_cud_event(event: Event, users: AsyncIOMotorCollection):
    match event.name:
        case events.USER_CREATED_EVENT:
            user = UserModel(**event.data)
            await create_user(users, user)
        case events.USER_UPDATED_EVENT:
            user = UserModel(**event.data)
            if user.id is not None:
                logger.info('Checking if user exists')
                res = await users.find_one({'_id': user.id})
                if not res:
                    await create_user(users, user)
                else:
                    update_params = UpdateUserModel(**event.data)
                    await users.update_one({'_id': user.pub_id}, {"$set": update_params.dict(exclude_unset=True)})
                    logger.info(f'User {user.pub_id} updated')
            else:
                logger.error('Got no `pub_id`')
        case events.USER_DELETED_EVENT:
            user_id = event.data.get('pub_id')
            if user_id is not None:
                delete_result = await users.delete_one({'_id': user_id})
                if delete_result.deleted_count == 1:
                    logger.info(f'User {user_id} was deleted')
            else:
                logger.error('Got no `pub_id`')


async def handle_biz_event(event: Event, users: AsyncIOMotorCollection):
    match event.name:
        case events.USER_ROLE_CHANGED:
            user_id = event.data.get('pub_id')
            logger.info(f'User {user_id} role changed')


async def consume_events(app: FastAPI):
    consumer = app.state.kafka_consumer
    users = get_user_collection(app)

    async for msg in consumer:
        data = unpack_data(msg.value)
        event = Event(**data)
        logger.info(f'Got {event.name} event {event.id}')
        if msg.key == KAFKA_USER_CUD_EVENT_KEY:
            await handle_cud_event(event, users)
        elif msg.key == KAFKA_USER_BIZ_EVENT_KEY:
            await handle_biz_event(event, users)
