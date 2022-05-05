import datetime
import secrets
import hashlib
import random
from sqlalchemy.orm import Session

from notes import models
from notes import schemas


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> schemas.User:
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
        password_hash_algo='pbkdf2',
        salt=salt,
        created_time=now,
        updated_time=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_notes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Note).offset(skip).limit(limit).all()


def create_note(db: Session, note: schemas.NoteCreate, username: str):
    user = get_user_by_username(db, username)
    now = datetime.datetime.now()
    db_note = models.Note(**note.dict(), user_id=user.id, created_time=now, updated_time=now)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def create_tag(db: Session, tag: schemas.TagCreate):
    now = datetime.datetime.now()
    tag_dict = tag.dict()

    if tag_dict.get('color') is None:
        tag_dict['color'] = f"#{int.from_bytes(random.randbytes(3), 'little'):06x}"

    db_tag = models.Tag(**tag_dict, created_time=now, updated_time=now)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()
