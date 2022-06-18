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


def read_by_ids(db: Session, ids: list[int], error_if_not_all_exists: bool = False) -> list[models.Note]:
    notes = db.query(models.Note).filter(models.Note.id.in_(ids)).all()
    if set(ids) != {note.id for note in notes}:
        raise crud.exceptions.NoteNotExistsError
    return notes


def read_by_tag(db: Session, tag: str, not_found_error: bool = False) -> models.Note:
    db_tag = db.query(models.Note).filter(models.Note.tag == tag).first()
    if db_tag is None and not_found_error:
        raise crud.exceptions.TagNotExistsError
    return db_tag


def read_by_tags(db: Session, tags: list[str], not_found_error: bool = False) -> list[models.Note]:
    db_tags = db.query(models.Note).filter(models.Note.tag.in_(tags)).all()
    if set(tags) != {tag.tag for tag in db_tags}:
        raise crud.exceptions.TagNotExistsError
    return db_tags


def read_tags(db: Session) -> list[models.Note]:
    return db.query(models.Note).filter(models.Note.tag.is_not(None)).all()


def create(
    db: Session,
    note: schemas.NoteCreate,
    authenticated_username: str | None = None,
) -> models.Note:
    now = datetime.datetime.now()

    if authenticated_username is None:
        authenticated_username = 'anon'
    user = crud.user.read_by_username(db, authenticated_username)

    note_dict = note.dict()

    if note.color is None or note.color == '#000000':
        note_dict['color'] = colortool.random_hex()

    note_dict['right_notes'] = []

    if note.tag and read_by_tag(db, note.tag) is not None:
        raise crud.exceptions.TagAlreadyExists

    if note.tags:
        tags = read_by_tags(db, note.tags, not_found_error=True)
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
) -> models.Note:

    db_note = read_by_id(db, note_id)
    if db_note is None:
        raise crud.exceptions.NoteNotExistsError
    if db_note.user.username == 'anon':
        raise crud.exceptions.AnonNotesCantBeUpdated
    elif db_note.user.username != authenticated_username:
        raise crud.exceptions.UserIsNotAllowedToEditOtherUserNotes

    now = datetime.datetime.now()

    # update only not None fields keep old values

    special_handle = {'tag', 'tags'}
    for k, v in note.dict().items():
        if v is None:
            continue
        if k in special_handle:
            continue
        setattr(db_note, k, v)


    # if note.text:
    #     db_note.text = note.text
    # db_note.url = note.url
    # db_note.is_private = note.is_private
    # db_note.is_archived = note.is_archived
    # db_note.tag = note.tag
    # db_note.color = note.color
    db_note.updated_time = now

    # all_tags = read_tags(db)

    # if note.tag: no checks are necessary, because you can create any tag name you want (new tag)
    # if note.tag on update/create - you should check that there's only 1 note with that tag
    # rely on database constraints ?

    # if note.tags:
    #     ...
    #
    #
    # if note.right_notes:
    #     ...
    #
    # if unknown_tags := set(note.tags) - {tag.name for tag in tags}:
    #     raise crud.exceptions.TagNotExistsError(list(unknown_tags))
    #
    # for tag in tags:
    #     tag.updated_time = now
    #
    # db_note.right_notes = tags

    db.commit()
    db.refresh(db_note)
    return db_note
