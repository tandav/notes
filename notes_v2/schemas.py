import datetime
from pydantic import BaseModel, root_validator, validator
from fastapi.security import HTTPBasicCredentials


# class UserBase(BaseModel):
#     username: str


UserCreate = HTTPBasicCredentials


# class User(UserBase):
class User(BaseModel):
    username: str
    id: int
    created_time: datetime.datetime
    updated_time: datetime.datetime

    class Config:
        orm_mode = True
