from common.helpers import prepare_mongo_db, set_task_collection, set_user_collection
from fastapi import FastAPI

from .config import config
from .handler import router


def create_app() -> FastAPI:
    app = FastAPI(title='Task tracker')

    @app.on_event('startup')
    async def setup_clients() -> None:  # pylint: disable=W0612
        mongo_client, mongo_db = prepare_mongo_db(config.mongo_connection_str, config.mongo_db_name)
        app.mongo_client = mongo_client
        app.config = config
        set_task_collection(app, mongo_db)
        set_user_collection(app, mongo_db)
        app.task_collection.create_index('pub_id')

    @app.on_event('shutdown')
    async def shutdown_clients() -> None:  # pylint: disable=W0612
        app.mongo_client.close()

    app.include_router(router, tags=['Tasks'], prefix='/tasks')

    return app
