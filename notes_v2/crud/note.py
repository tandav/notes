import datetime

import colortool
from sqlalchemy.exc import IntegrityError
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


def read_by_ids(db: Session, ids: list[int], not_found_error: bool = False) -> list[models.Note]:
    notes = db.query(models.Note).filter(models.Note.id.in_(ids)).all()
    if not_found_error and set(ids) != {note.id for note in notes}:
        raise crud.exceptions.NoteNotExistsError
    return notes


def read_by_tag(db: Session, tag: str, not_found_error: bool = False) -> models.Note:
    db_tag = db.query(models.Note).filter(models.Note.tag == tag).first()
    if not_found_error and db_tag is None:
        raise crud.exceptions.TagNotExistsError
    return db_tag


def read_by_tags(db: Session, tags: list[str], not_found_error: bool = False) -> list[models.Note]:
    db_tags = db.query(models.Note).filter(models.Note.tag.in_(tags)).all()
    if not_found_error and set(tags) != {tag.tag for tag in db_tags}:
        raise crud.exceptions.TagNotExistsError
    return db_tags


def read_tags(db: Session) -> list[models.Note]:
    return db.query(models.Note).filter(models.Note.tag.is_not(None)).all()


# def handle_tags_for_create_or_update(db: Session, note: schemas.NoteCreate, action: str, note_id: int | None = None):
#     if note.tags is not None:
#         raise NotImplementedError


# def handle_right_notes_and_tags(db: Session, note: schemas.NoteCreate | schemas.NoteUpdate) -> dict:
#     note_dict = note.dict()
#     note_dict['right_notes'] = []
#
#     if note.tags:
#         tags = read_by_tags(db, note.tags, not_found_error=True)
#         note_dict['right_notes'] += tags
#
#     if note.right_notes:
#         note_dict['right_notes'] += read_by_ids(db, note.right_notes)
#     del note_dict['tags']
#     return note_dict


def create(
    db: Session,
    note: schemas.NoteCreate,
    authenticated_username: str | None = None,
) -> models.Note:
    now = datetime.datetime.now()

    if authenticated_username is None:
        authenticated_username = 'anon'
    user = crud.user.read_by_username(db, authenticated_username)

    if note.tag:
        already_existing_tag = read_by_tag(db, note.tag)
        if already_existing_tag is not None:
            raise crud.exceptions.TagAlreadyExists

    note_dict = note.dict()
    right_notes = []
    if note.tags:
        right_notes += read_by_tags(db, note.tags, not_found_error=True)
    if note.right_notes:
        right_notes += read_by_ids(db, note.right_notes, not_found_error=True)
    for ref_note in right_notes:
        ref_note.updated_time = now
    note_dict['right_notes'] = right_notes
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

    return db_note


def update(
    note_id: int,
    note: schemas.NoteUpdate,
    db: Session,
    authenticated_username: str | None = None,
) -> models.Note:

    db_note = read_by_id(db, note_id)
    if db_note is None:
        raise crud.exceptions.NoteNotExistsError
    if db_note.user.username == 'anon':
        raise crud.exceptions.AnonNotesCantBeUpdated
    elif db_note.user.username != authenticated_username:
        raise crud.exceptions.UserIsNotAllowedToEditOtherUserNotes

    now = datetime.datetime.now()

    if note.tag:
        already_existing_tag = read_by_tag(db, note.tag)
        if already_existing_tag is not None and already_existing_tag.id != note_id:
            raise crud.exceptions.TagAlreadyExists

    # update only not None fields keep old values
    special_handle = {'tags', 'right_notes'}
    for k, v in note.dict().items():
        if v is None:
            continue
        if k in special_handle:
            continue
        setattr(db_note, k, v)

    right_notes = []

    if note.tags:
        right_notes += read_by_tags(db, note.tags, not_found_error=True)

    if note.right_notes:
        right_notes += read_by_ids(db, note.right_notes, not_found_error=True)

    for ref_note in right_notes:
        if ref_note in db_note.right_notes:
            continue
        ref_note.updated_time = now

    db_note.right_notes = right_notes
    db_note.updated_time = now

    db.commit()
    db.refresh(db_note)
    return db_note
