import datetime
import string

import colortool
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
    text: str | None = None
    url: AnyUrl | None = None
    is_private: bool = True
    is_archived: bool = False
    tag: str | None = None
    color: str | None = None
    # tags: list[Tag] = []
    right_notes: list[int] = []
    left_notes: list[int] = []
    tags: list[str] = []

    # tag
    # right_notes: list[str] = []

    @validator('tag')
    def validate_tag(cls, v):
        if v is None:
            return v
        if v == '':
            raise ValueError('tag name cant be empty')
        if not set(v) <= set(string.ascii_letters + string.digits + '-_'):
            raise ValueError('tag name can only contain letters, digints and "_", "-" special characters')
        if not v[0].isalpha():
            raise ValueError('tag name should must start with a letter')
        return v

    @validator('color')
    def color_string_check(cls, v):
        if v is None:
            return v
        v = v.lower()
        if not colortool.is_hex_color(v):
            raise ValueError('invalid color. Provide color in #f048ed format')
        return v


class NoteCreate(NoteBase):
    @root_validator(pre=True)
    def validate_tag_color(cls, values):
        if values.get('tag') is None and values.get('color') is not None:
            raise ValueError('color is not None but tag is None. Cant assign color for tag == None')
        return values

    @validator('color', always=True)
    def handle_default_color(cls, v):
        if v is None or v == '#000000':
            v = colortool.random_hex()
        return v


class NoteUpdate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    user_id: int
    username: str
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True


# ================================================================


# class Node(BaseModel):
#     id: int
#     # data: Json
#     data: dict
#
#     class Config:
#         orm_mode = True
