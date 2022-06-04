import datetime

from fastapi.security import HTTPBasicCredentials
from pydantic import AnyUrl
from pydantic import BaseModel
from pydantic import Json
from pydantic import root_validator
from pydantic import validator

# class UserBase(BaseModel):
#     username: str


UserCreate = HTTPBasicCredentials

# ================================================================

# class User(UserBase):


class User(BaseModel):
    username: str
    id: int
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True

# ================================================================


class Message(BaseModel):
    detail: str


# ================================================================


class NoteBase(BaseModel):
    # title: str | None = None
    text: str | None = None
    url: AnyUrl | None = None
    is_private: bool = True
    # tags: list[Tag] = []
    tags: list[str] = []
    # right_notes: list[str] = []


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    user_id: int
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True


# ================================================================


class Node(BaseModel):
    id: int
    # data: Json
    data: dict

    class Config:
        orm_mode = True
