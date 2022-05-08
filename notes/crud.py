import datetime
import secrets
import hashlib
import random
from sqlalchemy.orm import Session

from notes import models
from notes import schemas


class CrudError(BaseException): pass
class TagNotExistsError(CrudError): pass
class NoteNotExistsError(CrudError): pass


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
        # password_hash_algo='pbkdf2',
        salt=salt,
        created_time=now,
        updated_time=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_note(db: Session, note_id: int):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if note is None:
        raise NoteNotExistsError(note_id)
    return note


def get_tag(db: Session, name: str):
    tag = db.query(models.Tag).filter(models.Tag.name == name).first()
    return tag


def get_notes(db: Session, skip: int = 0, limit: int = 100):
    return [note.to_dict() for note in db.query(models.Note).order_by(models.Note.id.desc()).offset(skip).limit(limit).all()]


def delete_note(db: Session, note_id: int):
    db.query(models.Note).filter(models.Note.id == note_id).delete()
    db.commit()


def delete_tag(db: Session, name: str):
    db.query(models.Tag).filter(models.Tag.name == name).delete()
    db.commit()


def create_note(db: Session, note: schemas.NoteCreate, username: str):
    user = get_user_by_username(db, username)
    now = datetime.datetime.now()
    note_dict = note.dict()

    if note.tags:
        tags = db.query(models.Tag).filter(models.Tag.name.in_(note.tags)).all()
        if unknown_tags := set(note.tags) - {tag.name for tag in tags}:
            raise TagNotExistsError(list(unknown_tags))
        note_dict = {**note.dict(), 'tags': tags}

    db_note = models.Note(**note_dict, user_id=user.id, created_time=now, updated_time=now)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note.to_dict()


def edit_note(db: Session, note: schemas.NoteCreate, note_id: int):
    db_note = get_note(db, note_id)
    db_note.text = note.text
    db_note.url = note.url
    db_note.updated_time = datetime.datetime.now()

    # if note.tags:
    #     breakpoint()
    tags = db.query(models.Tag).filter(models.Tag.name.in_(note.tags)).all()
    if unknown_tags := set(note.tags) - {tag.name for tag in tags}:
        raise TagNotExistsError(list(unknown_tags))
    db_note.tags = tags
    db.commit()
    db.refresh(db_note)
    return db_note.to_dict()


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


def get_tags(db: Session):
    return db.query(models.Tag).all()
