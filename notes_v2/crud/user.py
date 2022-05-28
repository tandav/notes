from sqlalchemy.orm import Session
import datetime
import hashlib
import random
import secrets
from notes_v2 import models
from notes_v2 import schemas


def read_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


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
