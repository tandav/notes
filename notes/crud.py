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
    return db.query(models.Note).filter(models.Note.id == note_id).first()


def get_notes(db: Session, skip: int = 0, limit: int = 100):
    return [note.to_dict() for note in db.query(models.Note).order_by(models.Note.id.desc()).offset(skip).limit(limit).all()]


def delete_note(db: Session, note_id: int):
    db.query(models.Note).filter(models.Note.id == note_id).delete()


# def get_tags_by_names(db: Session, tags: list[str]):
#     return db.query(models.Tag).filter(models.Tag.name.in_(tags)).all()


def create_note(db: Session, note: schemas.NoteCreate, username: str):
    user = get_user_by_username(db, username)
    now = datetime.datetime.now()

    # sam = User()
    # sam.name = 'sam'
    # sam_teams = session.query(Teams).filter(Teams.name.in_(['wildcats', 'jokers'])).all()
    # sam.teams = [team for team in sam_teams]

    note_dict = note.dict()

    if note.tags:
        tags = db.query(models.Tag).filter(models.Tag.name.in_(note.tags)).all()
        if unknown_tags := set(note.tags) - {tag.name for tag in tags}:
            raise TagNotExistsError(list(unknown_tags))

        note_dict = {**note.dict(), 'tags': tags}

    db_note = models.Note(**note_dict, user_id=user.id, created_time=now, updated_time=now)
    # db_note.tags = [tag for tag in db.query(models.Tag).filter(models.Tag.name.in_([note.tags])).all()]

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # convert tags to str befor return
    # db_note.tags = [tag.name for tag in db_note.tags]
    # if note.tags:
    #     breakpoint()
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


def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()


def get_tags(db: Session):
    return db.query(models.Tag).all()
