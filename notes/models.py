from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    password_hash_algo = Column(String)
    salt = Column(String)
    avatar = Column(String, nullable=True)
    notes = relationship("Note", back_populates="user")
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)


notes_tags = Table('notes_tags', Base.metadata,
    Column('note_id', ForeignKey('note.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
)

notes_attachments = Table('notes_attachments', Base.metadata,
    Column('note_id', ForeignKey('note.id'), primary_key=True),
    Column('attachment_id', ForeignKey('attachment.id'), primary_key=True),
)


class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    # username = Column(String, ForeignKey('user.username'))
    title = Column(String, index=True, nullable=True)
    text = Column(String, nullable=True)
    url = Column(String, nullable=True)
    is_private = Column(Boolean, nullable=False, default=False)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)

    user = relationship('User', back_populates="notes")
    tags = relationship('Tag', secondary=notes_tags, back_populates='notes')
    attachments = relationship('Attachment', secondary=notes_attachments, back_populates='notes')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)
    notes = relationship('Note', secondary=notes_tags, back_populates='tags')


class Attachment(Base):
    __tablename__ = 'attachment'

    id = Column(Integer, primary_key=True, index=True)
    # data = Column(text)
    notes = relationship('Note', secondary=notes_attachments, back_populates='attachments')
