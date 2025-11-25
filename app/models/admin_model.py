from pydantic import BaseModel
from .enums import AccessOption


class UserId(BaseModel):
    user_id: str


class UserIds(BaseModel):
    user_ids: list[str]


class SetMode(BaseModel):
    mode: AccessOption
