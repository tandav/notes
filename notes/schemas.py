from __future__ import annotations
import datetime
import string
from pydantic import BaseModel, validator, root_validator


# ===================================================================================


class NoteBase(BaseModel):
    title: str | None = None
    text: str | None = None
    url: str | None = None
    is_private: bool
    tags: list[Tag] = []

    @validator('url')
    def url_starts_with_http(cls, v):
        if v is not None and not v.startswith('http'):
            raise ValueError('url must starts with http')
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

    class Config:
        orm_mode = True

# ===================================================================================


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    notes: list[Note] = []
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True

# ===================================================================================


class TagBase(BaseModel):
    name: str
    color: str | None = None

    @validator('color')
    def color_string_check(cls, v):
        v = v.lower()
        if not (v.startswith('#') and set(v[1:]) <= set(string.hexdigits)):
            raise ValueError('invalid color. Provide color in #f048ed format')
        return v


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    notes: list[Note] = []
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True

Note.update_forward_refs()
NoteCreate.update_forward_refs()
# Tag.update_forward_refs()
