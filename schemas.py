from pydantic import BaseModel, validator, root_validator


class NoteBase(BaseModel):
    title: str | None = None
    text: str | None = None
    is_bookmark: bool

    @root_validator(pre=True)
    def text_not_null_for_bookmarks(cls, values):
        if values['is_bookmark'] and 'text' not in values:
            raise ValueError('text field should contain url (cant be empty)')
        return values

    @root_validator(pre=True)
    def bookmark_url_starts_with_http(cls, values):
        if values['is_bookmark'] and not values['text'].startswith('http://'):
            raise ValueError('url must starts with http://')
        return values

    @root_validator(pre=True)
    def title_and_text_cant_both_be_empty(cls, values):
        if 'title' not in values and 'text' not in values:
            raise ValueError('title_and_text_cant_both_be_empty')
        return values


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    user_id: int
    # username: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    notes: list[Note] = []

    class Config:
        orm_mode = True
