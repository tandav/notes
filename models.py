from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    notes = relationship("Note", back_populates="user")


notes_tags = Table('notes_tags', Base.metadata,
    Column('note_id', ForeignKey('note.id'), primary_key=True),
    Column('note_id', ForeignKey('tag.id'), primary_key=True)
)


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, index=True, nullable=True)
    text = Column(String, nullable=True) # for bookmarks this should be url
    user = relationship('User', back_populates="notes")
    tags = relationship('Tag', secondary=notes_tags, back_populates='notes')
    is_bookmark = Column(Boolean, nullable=False)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)


class Tag(Base):
    id = Column(Integer, primary_key=True, index=True)
    notes = relationship('Note', secondary=notes_tags, back_populates='tags')
