import datetime

import colortool
from sqlalchemy.orm import Session

import notes_v2.crud.user
from notes_v2 import crud
from notes_v2 import models
from notes_v2 import schemas


def read_by_id(db: Session, id: int) -> models.Note:
    return db.query(models.Note).filter(models.Note.id == id).first()


def read_many(db: Session, skip: int = 0, limit: int = 100) -> list[models.Note]:
    return db.query(models.Note).offset(skip).limit(limit).all()


def read_by_ids(db: Session, ids: list[int]) -> list[models.Note]:
    return db.query(models.Note).filter(models.Note.id.in_(ids)).all()


def read_by_tag(db: Session, tag: str) -> models.Note:
    return db.query(models.Note).filter(models.Note.tag == tag).first()


def read_by_tags(db: Session, tags: list[str]) -> list[models.Note]:
    return db.query(models.Note).filter(models.Note.tag.in_(tags)).all()


def read_tags(db: Session) -> list[models.Note]:
    return db.query(models.Note).filter(models.Note.tag.is_not(None)).all()


def create(
    db: Session,
    note: schemas.NoteCreate,
    authenticated_username: str | None = None,
):
    now = datetime.datetime.now()

    if authenticated_username is None:
        authenticated_username = 'anon'
    user = crud.user.read_by_username(db, authenticated_username)

    note_dict = note.dict()

    if note.color is None or note.color == '#000000':
        note_dict['color'] = colortool.random_hex()

    note_dict['right_notes'] = []

    if note.tags:
        tags = read_by_tags(db, note.tags)
        note_dict['right_notes'] += tags

    if note.right_notes:
        note_dict['right_notes'] += read_by_ids(db, note.right_notes)
    del note_dict['tags']
    db_note = models.Note(
        **note_dict,
        user=user,
        created_time=now,
        updated_time=now,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note.to_dict()


def update(
    note_id: int,
    note: schemas.NoteCreate,
    db: Session,
    authenticated_username: str | None = None,
):
    pass
