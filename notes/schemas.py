from __future__ import annotations

import datetime
import string

from pydantic import BaseModel, root_validator, validator

from notes.util import is_hex_color

# ===================================================================================


class NoteBase(BaseModel):
    # title: str | None = None
    text: str | None = None
    url: str | None = None
    # is_private: bool
    # tags: list[Tag] = []
    tags: list[str] = []

    @validator('url')
    def validate_url(cls, v):
        if v is None:
            return v
        if not v.startswith('http'):
            raise ValueError('url must starts with http')
        if ' ' in v:
            raise ValueError('url cant contain spaces')
        return v

    # @root_validator(pre=True)
    # def text_not_null_for_bookmarks(cls, values):
    #     if values['is_bookmark'] and 'text' not in values:
    #         raise ValueError('text field should contain url (cant be empty)')
    #     return values
    #
    # @root_validator(pre=True)
    # def bookmark_url_starts_with_http(cls, values):
    #     if values['is_bookmark'] and not values['text'].startswith('http://'):
    #         raise ValueError('url must starts with http://')
    #     return values
    #
    # @root_validator(pre=True)
    # def title_and_text_cant_both_be_empty(cls, values):
    #     if 'title' not in values and 'text' not in values:
    #         raise ValueError('title_and_text_cant_both_be_empty')
    #     return values


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    user_id: int
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True

# ===================================================================================


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    # notes: list[Note] = []
    # notes: list[str] = []
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True

# ===================================================================================


class TagBase(BaseModel):
    name: str
    color: str | None = None

    @validator('name')
    def not_empty(cls, v):
        if v == '':
            raise ValueError('tag name cant be empty')
        return v

    @validator('name')
    def valid_characters(cls, v):
        if not set(v) <= set(string.ascii_letters + string.digits + '-_'):
            raise ValueError('tag name can only contain letters, digints and "_", "-" special characters')
        return v

    @validator('name')
    def startswith_letter(cls, v):
        if not v[0].isalpha():
            raise ValueError('tag name should must start with a letter')
        return v

    @validator('color')
    def color_string_check(cls, v):
        if v is None:
            return v
        v = v.lower()
        if not is_hex_color(v):
            raise ValueError('invalid color. Provide color in #f048ed format')
        return v


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    color: str
    # notes: list[Note] = []
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True

NoteCreate.update_forward_refs()
Note.update_forward_refs()
# Tag.update_forward_refs()

# ===================================================================================


class Message(BaseModel):
    detail: str
