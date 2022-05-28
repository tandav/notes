from http import HTTPStatus
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException
from fastapi import APIRouter
from sqlalchemy.orm import Session

from notes_v2 import crud
from notes_v2 import schemas
from notes_v2.dependencies import get_db
from notes_v2.dependencies import http_basic
from notes_v2.dependencies import http_basic_optional

router = APIRouter()


@router.post("/users/", response_model=schemas.User)
def create_user(credentials: HTTPBasicCredentials = Depends(http_basic), db: Session = Depends(get_db)):
    db_user = crud.user.read_by_username(db, username=credentials.username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="username already registered")
    return crud.user.create(db=db, user=credentials)
