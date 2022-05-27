import logging
from asyncio import Future
from asyncio.log import logger

from aiokafka import AIOKafkaProducer
from common.kafka.events import USER_CREATED_EVENT, USER_DELETED_EVENT, USER_ROLE_CHANGED, USER_UPDATED_EVENT
from common.kafka.models import Event
from common.kafka.serialization import pack_data
from common.kafka.topics import KAFKA_USER_BIZ_EVENT_KEY, KAFKA_USER_CUD_EVENT_KEY, KAFKA_USER_TOPIC

logger = logging.getLogger('uvicorn')


class KafkaProducerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs) -> AIOKafkaProducer:
        if cls._instance is None:
            cls._instance = AIOKafkaProducer(*args, **kwargs)
        return cls._instance


def prepare_msg(data: dict, event_name: str):
    event = Event(name=event_name, data=data)
    return pack_data(event.dict())


async def send_cud_event(data: dict, event: str) -> Future:
    logger.info(f'Sending {event} CUD event')
    return await KafkaProducerSingleton._instance.send(
        KAFKA_USER_TOPIC, prepare_msg(data, event), key=KAFKA_USER_CUD_EVENT_KEY
    )


async def send_biz_event(data: dict, event: str) -> Future:
    logger.info(f'Sending {event} BIZ event')
    return await KafkaProducerSingleton._instance.send(
        KAFKA_USER_TOPIC, prepare_msg(data, event), key=KAFKA_USER_BIZ_EVENT_KEY
    )


async def send_user_created_event(data: dict) -> Future:
    return await send_cud_event(data, USER_CREATED_EVENT)


async def send_user_updated_event(data: dict) -> Future:
    return await send_cud_event(data, USER_UPDATED_EVENT)


async def send_user_deleted_event(data: dict) -> Future:
    return await send_cud_event(data, USER_DELETED_EVENT)


async def send_user_role_changed_event(data: dict) -> Future:
    return await send_biz_event(data, USER_ROLE_CHANGED)
