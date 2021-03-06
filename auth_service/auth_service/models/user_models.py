import datetime

from bson import ObjectId
from common.constants import UserRole
from common.helpers import gen_uuid
from common.models import PyObjectId
from pydantic import BaseModel, EmailStr, Field


class CreateUserModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    role: UserRole = Field(...)
    email: EmailStr = Field(...)
    name: str | None

    class Config:
        use_enum_values = True


class UserModel(CreateUserModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    pub_id: str = Field(default_factory=gen_uuid)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    is_active: bool = Field(default=True)

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: PyObjectId}

    def get_public_dict(self) -> dict:
        return self.dict(exclude={'id': True, 'password': True})


class UpdateUserModel(BaseModel):
    username: str | None
    password: str | None
    role: UserRole | None
    email: EmailStr | None
    name: str | None
    is_active: bool | None

    class Config:
        use_enum_values = True
        extra = 'forbid'

    def get_public_dict(self) -> dict:
        return self.dict(exclude={'id': True, 'password': True}, exclude_unset=True)


class UserModelOut(BaseModel):
    pub_id: str = Field(...)
    username: str = Field(...)
    name: str | None
    role: UserRole = Field(...)
    email: EmailStr = Field(...)

    class Config:
        use_enum_values = True
