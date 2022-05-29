import datetime
import hashlib
import secrets

from sqlalchemy.orm import Session

from notes_v2 import models
from notes_v2 import schemas


def read_many(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Node).offset(skip).limit(limit).all()


# def read_by_username(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()
#
#
def create(db: Session):
    now = datetime.datetime.now()
    db_node = models.Node(
        data={'hello': 1, 'world': 2, 'created_time': now.isoformat(), 'id': 42},
        # username=user.username,
        # password=password_hashed,
        # salt=salt,
        # created_time=now,
        # updated_time=now,
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node
