class CrudError(BaseException): pass
class TagNotExistsError(CrudError): pass
class NoteNotExistsError(CrudError): pass
class NoteAlreadyArchived(CrudError): pass
class NoteAlreadyUnarchived(CrudError): pass
class AnonNotesCantBeUpdated(CrudError): pass
class UserIsNotAllowedToEditOtherUserNotes(CrudError): pass
