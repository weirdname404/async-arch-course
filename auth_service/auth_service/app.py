import logging

from common.constants import UserRole
from common.helpers import get_user_collection, prepare_mongo_db, set_user_collection
from common.models import PyObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorCollection

from . import config
from .api.auth_handler import router as auth_router
from .api.user_handler import router as user_router
from .models.user_models import UserModel
from .security import create_user_safely

logger = logging.getLogger('uvicorn')
origins = [
    config.TASK_TRACKER_URL,
]


async def _create_superuser(users: AsyncIOMotorCollection) -> UserModel:
    superuser = UserModel(
        id=PyObjectId("627d7c1501a6b2ef17fa25ab"),
        pub_id="0a9c5bfe-af63-457b-811b-c1cdcd375222",
        username='admin',
        password='admin',
        role=UserRole.ADMIN,
        email='admin@admin.com',
    )
    exist_user = await users.find_one({'pub_id': superuser.pub_id})
    if exist_user is None:
        logger.info('Creating superuser...')
        await create_user_safely(users, superuser)
        exist_user = await users.find_one({'_id': superuser.id})
    else:
        logger.info('Superuser exists...')

    user_model = UserModel(**exist_user)
    return user_model


def create_app() -> FastAPI:
    app = FastAPI(title='Auth and user service')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event('startup')
    async def setup_clients() -> None:  # pylint: disable=W0612
        mongo_client, mongo_db = prepare_mongo_db(config.MONGO_CONNECTION, config.MONGO_DB_NAME)
        app.state
        app.state.mongo_client = mongo_client
        set_user_collection(app, mongo_db)
        get_user_collection(app).create_index('username')

    @app.on_event('startup')
    async def create_superuser() -> None:
        await _create_superuser(get_user_collection(app))

    @app.on_event('shutdown')
    async def shutdown_clients() -> None:  # pylint: disable=W0612
        app.state.mongo_client.close()

    app.include_router(auth_router, tags=['Auth'], prefix='/auth')
    app.include_router(user_router, tags=['Users'], prefix='/users')

    return app
