from sqlalchemy.orm import Session

import models
import schemas
import datetime


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, hashed_password=fake_hashed_password)
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
