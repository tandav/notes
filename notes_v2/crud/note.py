import datetime

from sqlalchemy.orm import Session

from notes_v2 import models
from notes_v2 import schemas


def read_many(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Node).offset(skip).limit(limit).all()


# def create(db: Session):
#     now = datetime.datetime.now()
#     user = httpbasic credentials
#     db_node = models.Note(
#
#     )
#     db.add(db_node)
#     db.commit()
#     db.refresh(db_node)
#     return db_node
