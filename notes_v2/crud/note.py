import datetime

import colortool
from sqlalchemy.orm import Session

import notes_v2.crud.exceptions
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


# def update(
#     note_id: int,
#     note: schemas.NoteCreate,
#     db: Session,
#     authenticated_username: str | None = None,
# ):
#     db_note = read_by_id(db, note_id)
#     if db_note is None:
#         raise crud.exceptions.NoteNotExistsError
#     if db_note.user.username == 'anon':
#         raise crud.exceptions.AnonNotesCantBeUpdated
#     elif db_note.user.username != authenticated_username:
#         raise crud.exceptions.UserIsNotAllowedToEditOtherUserNotes
#
#     now = datetime.datetime.now()
#     db_note.text = note.text
#     db_note.url = note.url
#     db_note.is_private = note.is_private
#     db_note.is_archived = note.is_archived
#     db_note.tag = note.tag
#     db_note.color = note.color
#     db_note.updated_time = now
#
#     all_tags = read_tags(db)
#
#     # if note.tag: no checks are necessary, because you can create any tag name you want (new tag)
#     # if note.tag on update/create - you should check that there's only 1 note with that tag
#     # rely on database constraints ?
#
#     if note.tags:
#         ...
#
#
#     if note.right_notes:
#         ...
#
#     if unknown_tags := set(note.tags) - {tag.name for tag in tags}:
#         raise crud.exceptions.TagNotExistsError(list(unknown_tags))
#
#     for tag in tags:
#         tag.updated_time = now
#
#     db_note.right_notes = tags
