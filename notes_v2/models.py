from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Computed
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ================================================================


note_to_note = Table(
    'note_to_note', Base.metadata,
    Column('left_note_id', Integer, ForeignKey('note.id'), primary_key=True),
    Column('right_note_id', Integer, ForeignKey('note.id'), primary_key=True),
)


class Note(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    is_private = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    text = Column(String, nullable=True)
    url = Column(String, nullable=True)
    tag = Column(String, unique=True, index=True, nullable=True)  # defines is tag/readme page if not null (kinda is_tag: considered tag if not null)
    color = Column(String, nullable=True)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    right_notes = relationship(
        'Note',
        secondary=note_to_note,
        primaryjoin=id == note_to_note.c.left_note_id,
        secondaryjoin=id == note_to_note.c.right_note_id,
        backref='left_notes',
    )
    user = relationship('User', back_populates='notes')

    def to_dict(self):
        return {
            'id': self.id,
            'is_private': self.is_private,
            'is_archived': self.is_archived,
            'text': self.text,
            'url': self.url,
            'tag': self.tag,
            'color': self.color,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'user_id': self.user_id,
            'username': self.user.username,
            'right_notes': [note.id for note in self.right_notes],
            'left_notes': [note.id for note in self.left_notes],
            'tags': [note.tag for note in self.right_notes if note.tag is not None],
        }


# ================================================================


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    salt = Column(String)
    notes = relationship('Note', back_populates='user')
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)


# ================================================================


# class Node(Base):
#     __tablename__ = 'node'
#     id = Column(Integer, primary_key=True, index=True)
#     data = Column(JSON)
#     # id = Column(Integer, Computed("json_extract(data, '$.id')", persisted=False), unique=True, nullable=False)
#     # __mapper_args__ = {
#     #     'primary_key': id,
#     # }
