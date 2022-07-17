import datetime
import hashlib
import secrets

from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

import notes_v2.crud.exceptions
from notes_v2 import crud
from notes_v2 import models
from notes_v2 import schemas


def read_many(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def read_by_username(db: Session, username: str, not_found_error: bool = False):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not_found_error and db_user is None:
        raise crud.exceptions.UserNotExistsError
    return db_user


def create(db: Session, user: schemas.UserCreate) -> schemas.User:
    now = datetime.datetime.now()
    salt = secrets.token_hex(8)
    password_hashed = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=user.password.encode(),
        salt=salt.encode(),
        iterations=500_000,
    )
    db_user = models.User(
        username=user.username,
        password=password_hashed,
        salt=salt,
        created_time=now,
        updated_time=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def check_credentials(db: Session, credentials: HTTPBasicCredentials) -> bool:
    user = read_by_username(db, credentials.username)
    if user is None:
        return False
    if hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=credentials.password.encode(),
        salt=user.salt.encode(),
        iterations=500_000,
    ) != user.password:
        return False
    return True
