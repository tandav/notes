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

# TODO: maybe set prefix /users here is a good idea
# https://fastapi.tiangolo.com/tutorial/bigger-applications/?h=files#another-module-with-apirouter
router = APIRouter(
    tags=['nodes'],
)

templates = Jinja2Templates(directory='notes_v2/templates')
templates.env.filters['format_time'] = util.format_time


@router.post('/nodes/', response_model=schemas.Node)
def create_node(db: Session = Depends(get_db)):
    """Create a user using username and password
    if user already exists returns an error
    """
    # db_user = crud.user.read_by_username(db, username=credentials.username)
    # if db_user:
    #     raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='username already registered')
    return crud.node.create(db=db)
