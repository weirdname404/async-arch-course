import datetime

from pydantic import BaseModel, Field

from ..helpers import gen_uuid


class Event(BaseModel):
    id: str = Field(default_factory=gen_uuid)
    name: str
    data: dict | None
    time: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    version: int = 1
