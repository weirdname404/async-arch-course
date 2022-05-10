import datetime

from common.constants import TaskStatus, UserRole
from common.helpers import gen_id
from common.models import PyObjectId
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class CreateTaskModel(BaseModel):
    status: TaskStatus | None = Field(default=TaskStatus.OPEN, description='Task status open/closed 0/1')
    description: str = Field(...)
    assignee_id: str = Field(...)

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class TaskModel(CreateTaskModel):
    _id: PyObjectId = Field(default_factory=PyObjectId)
    pub_id: Annotated[str, Field(default_factory=gen_id)]
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class UpdateTaskModel(BaseModel):
    description: str | None
    status: TaskStatus | None

    class Config:
        use_enum_values = True
        validate_assignment = True
        extra = 'forbid'


class UserModel(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId)
    pub_id: str = Field(...)
    role: UserRole

    class Config:
        use_enum_values = True
