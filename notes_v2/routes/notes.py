from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from notes_v2 import crud
from notes_v2 import schemas
from notes_v2 import util

# from notes_v2.util import header
from notes_v2.dependencies import get_db
from notes_v2.dependencies import guess_type
from notes_v2.dependencies import http_basic
from notes_v2.dependencies import http_basic_optional

router = APIRouter(
    tags=['notes'],
)


@router.post('/notes/', response_model=schemas.Node)
def create_note(db: Session = Depends(get_db)):
    return crud.node.create(db=db)
