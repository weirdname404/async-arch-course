from common.auth import Auth, auth_user_factory
from fastapi.security import OAuth2PasswordBearer

from .. import config
from ..models.user_models import UserModel

auth: Auth = auth_user_factory(
    oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login"),
    secret_key=config.SECRET_KEY,
    algorithm=config.ALGORITHM,
    user_model=UserModel,
)
