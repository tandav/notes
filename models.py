from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    notes = relationship("Note", back_populates="user")


notes_tags = Table('notes_tags', Base.metadata,
    Column('note_id', ForeignKey('note.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
)


class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    # username = Column(String, ForeignKey('user.username'))
    title = Column(String, index=True, nullable=True)
    text = Column(String, nullable=True)
    is_bookmark = Column(Boolean, nullable=False)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)

    user = relationship('User', back_populates="notes")
    tags = relationship('Tag', secondary=notes_tags, back_populates='notes')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, index=True)
    notes = relationship('Note', secondary=notes_tags, back_populates='tags')
