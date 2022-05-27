import asyncio

from aiokafka import AIOKafkaConsumer
from common.helpers import (
    get_task_collection,
    get_user_collection,
    prepare_mongo_db,
    set_task_collection,
    set_user_collection,
)
from common.kafka.topics import KAFKA_USER_TOPIC
from fastapi import FastAPI

from . import config
from .consumer import consume_events
from .handler import router


async def _setup_mongo(app: FastAPI) -> None:
    mongo_client, mongo_db = prepare_mongo_db(config.MONGO_CONNECTION, config.MONGO_DB_NAME)
    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_db
    set_user_collection(app, mongo_db)
    set_task_collection(app, mongo_db)
    get_user_collection(app).create_index('pub_id')
    get_task_collection(app).create_index('pub_id')


async def _setup_kafka(app: FastAPI) -> None:
    app.state.kafka_consumer = AIOKafkaConsumer(
        KAFKA_USER_TOPIC, bootstrap_servers=config.KAFKA_URL, group_id='task_tracker'
    )
    await app.state.kafka_consumer.start()


def create_app() -> FastAPI:
    app = FastAPI(title='Task tracker')

    @app.on_event('startup')
    async def setup_clients() -> None:  # pylint: disable=W0612
        await _setup_mongo(app)
        await _setup_kafka(app)

    @app.on_event('startup')
    async def start_consumer() -> None:
        asyncio.get_running_loop().create_task(consume_events(app))

    @app.on_event('shutdown')
    async def shutdown_clients() -> None:  # pylint: disable=W0612
        app.state.mongo_client.close()
        await app.state.kafka_consumer.stop()

    app.include_router(router, tags=['Tasks'], prefix='/tasks')

    return app
