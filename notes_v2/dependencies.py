from http import HTTPStatus

from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from notes_v2.crud.user import check_credentials
from notes_v2.database import SessionLocal
from notes_v2.database import engine


def get_db():
    db = SessionLocal()
    yield db
    db.close()


http_basic = HTTPBasic()
http_basic_optional = HTTPBasic(auto_error=False)

WrongUsernameOrPassword = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="username not exists or incorrect password",
    headers={"WWW-Authenticate": "Basic"},
)


def _authenticate(db: Session, credentials: HTTPBasicCredentials, optional: bool) -> str | None:
    if credentials is None:
        if optional:
            return
        else:
            raise WrongUsernameOrPassword
    elif not check_credentials(db, credentials):
        raise WrongUsernameOrPassword
    return credentials.username


def authenticate_optional(
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(http_basic_optional),
) -> str | None:
    return _authenticate(db, credentials, optional=True)


def authenticate(
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(http_basic),
) -> str:
    return _authenticate(db, credentials, optional=False)


def guess_type(accept=Header(default='application/json')):
    accept = accept.split(',')
    if accept[0] == 'text/html':
        return 'html'
    elif 'application/json' in accept or '*/*' in accept:
        return 'json'
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail='415 Unsupported Media Type')
