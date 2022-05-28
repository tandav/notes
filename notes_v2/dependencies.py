import secrets
from notes_v2.database import SessionLocal, engine
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Header
from fastapi import HTTPException
from http import HTTPStatus
from fastapi.responses import JSONResponse


def get_db():
    db = SessionLocal()
    yield db
    db.close()


http_basic = HTTPBasic()
http_basic_optional = HTTPBasic(auto_error=False)


def guess_type(accept = Header(default='application/json')):
    accept = accept.split(',')
    if accept[0] == 'text/html':
        return 'html'
    elif 'application/json' in accept or '*/*' in accept:
        return 'json'
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail='415 Unsupported Media Type')
