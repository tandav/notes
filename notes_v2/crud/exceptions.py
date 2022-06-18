from http import HTTPStatus

from fastapi import HTTPException


class CrudError(BaseException):
    STATUS = None

    @classmethod
    @property
    def http(cls):
        return HTTPException(status_code=cls.STATUS, detail=cls.__name__)


class HttpNotFound(CrudError):
    STATUS = HTTPStatus.NOT_FOUND


class TagNotExistsError(HttpNotFound): pass
class NoteNotExistsError(HttpNotFound): pass
class NoteAlreadyArchived(CrudError): pass
class NoteAlreadyUnarchived(CrudError): pass
class AnonNotesCantBeUpdated(CrudError): pass
class UserIsNotAllowedToEditOtherUserNotes(CrudError): pass
