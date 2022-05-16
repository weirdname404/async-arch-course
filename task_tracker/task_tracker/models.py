import datetime

from bson import ObjectId
from common.constants import UserRole
from common.helpers import gen_hex
from common.models import PyObjectId
from pydantic import BaseModel, EmailStr, Field


class CreateTaskModel(BaseModel):
    is_open: bool = Field(default=True)
    title: str = Field(...)
    description: str | None
    assignee_id: str = Field(...)


class TaskModel(CreateTaskModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    pub_id: str = Field(default=gen_hex(short=True))
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: PyObjectId}


class UpdateTaskModel(BaseModel):
    description: str | None
    title: str | None
    is_open: bool | None

    class Config:
        extra = 'forbid'


class TaskModelOut(BaseModel):
    pub_id: str
    assignee_id: str
    title: str
    description: str | None
    is_open: bool
    created_at: str


class UserModel(BaseModel):
    id: str | None = Field(alias='_id')
    pub_id: str = Field(...)
    username: str | None
    email: EmailStr | None
    role: UserRole | None
    is_active: bool = Field(default=True)

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.pub_id


class UpdateUserModel(BaseModel):
    role: UserRole | None
    is_active: bool | None
    username: str | None
    email: EmailStr | None

    def dict(self, *args, **kwargs):
        kwargs['exclude_unset'] = True
        return super().dict(*args, **kwargs)
