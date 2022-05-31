from functools import partial
from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from notes_v2 import crud
from notes_v2 import schemas
from notes_v2 import util

# from notes_v2.util import header
from notes_v2.dependencies import WrongUsernameOrPassword
from notes_v2.dependencies import authenticate
from notes_v2.dependencies import authenticate_optional
from notes_v2.dependencies import get_db
from notes_v2.dependencies import guess_type
from notes_v2.dependencies import http_basic
from notes_v2.dependencies import http_basic_optional
from notes_v2.templates import templates

# TODO: maybe set prefix /users here is a good idea
# https://fastapi.tiangolo.com/tutorial/bigger-applications/?h=files#another-module-with-apirouter
router = APIRouter(
    tags=['users'],
)


@router.post('/users/', response_model=schemas.User)
def create_user(credentials: HTTPBasicCredentials = Depends(http_basic), db: Session = Depends(get_db)):
    """Create a user using username and password
    if user already exists returns an error
    """
    db_user = crud.user.read_by_username(db, username=credentials.username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='username already registered')
    return crud.user.create(db=db, user=credentials)


@router.get(
    '/users/',
    response_model=list[schemas.User],
    responses={200: {'content': {'text/html': {}}}},
)
def read_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    users = crud.user.read_many(db, skip=skip, limit=limit)
    if mediatype == 'json':
        return users
    return templates.TemplateResponse(
        'users.html', {
            'request': request,
            'users': [schemas.User.from_orm(u) for u in users],
            'authenticated_username': authenticated_username,
        },
    )


@router.get(
    '/users/{username}',
    response_model=schemas.User,
    responses={200: {'content': {'text/html': {}}}},
)
def read_user_by_name(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    db_user = crud.user.read_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    if mediatype == 'json':
        return db_user
    user = schemas.User.from_orm(db_user).dict()
    return templates.TemplateResponse(
        'user.html', {
            'request': request, **user,
                'authenticated_username': authenticated_username,
        },
    )


# ================================ auth ================================


@router.get('/signin')
def signin(username: str = Depends(authenticate)):
    return RedirectResponse('/users')


@router.get('/signout', response_class=HTMLResponse)
def signout():
    """https://stackoverflow.com/a/32325848/4204843"""
    return '''
    <h1>signing out...</h1>
    <script>
    fetch("/signin", {headers: {"Authorization": "Basic wrong_credentials"}})
    setTimeout(function () {
        window.location.href = '/'
    }, 200)
    </script>
    '''
