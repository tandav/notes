from sqlalchemy import Integer, ForeignKey, String, Column, Table, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

note_to_note = Table("note_to_note", Base.metadata,
    Column("left_note_id", Integer, ForeignKey("note.id"), primary_key=True),
    Column("right_note_id", Integer, ForeignKey("note.id"), primary_key=True)
)

class Note(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    is_private = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    tag = Column(String, unique=True, index=True, nullable=True)  # defines is tag/readme page if not null (kinda is_tag: considered tag if not null)
    color = Column(String, nullable=True)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)
    right_notes = relationship(
        "Note",
        secondary=note_to_note,
        primaryjoin=id==note_to_note.c.left_note_id,
        secondaryjoin=id==note_to_note.c.right_note_id,
        backref="left_notes"
    )


# ================================================================


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    salt = Column(String)
    notes = relationship("Note", back_populates="user")
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False, index=True)
