from functools import partial
from http import HTTPStatus

import colortool
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

import notes_v2.crud.exceptions
import notes_v2.crud.note
import notes_v2.crud.user
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
def create(credentials: HTTPBasicCredentials = Depends(http_basic), db: Session = Depends(get_db)):
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
def read_many(
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
    db_user = crud.user.read_by_username(db, username=username, not_found_error=True)
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


@router.get('/signup')
def signup(
    db: Session = Depends(get_db),
    credentials=Depends(http_basic),
):
    db_user = crud.user.read_by_username(db, username=credentials.username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='username already registered')
    crud.user.create(db, credentials)
    return RedirectResponse('/')


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

#
# @router.get(
#     '/users/{username}/notes',
#     response_model=list[schemas.Note],
#     responses={200: {'content': {'text/html': {}}}},
# )
# def read_user_notes(
#     request: Request,
#     username: str,
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
#     mediatype=Depends(guess_type),
#     authenticated_username: str | None = Depends(authenticate_optional),
#
# ):
#     tags = []
#     for tag in crud.note.read_tags(db):
#         tag_ = tag.to_dict()
#         font_color, border_color = colortool.font_border_colors(tag_['color'])
#         tag_['color_pale'] = colortool.lighter(tag_['color'], ratio=0.8)
#         tag_['font_color'] = font_color
#         tags.append(tag_)
#
#     notes = [schemas.Note(**n.to_dict()) for n in crud.note.read_by_username(db, username, authenticated_username, skip, limit)]
#     if mediatype == 'json':
#         return notes
#     return templates.TemplateResponse(
#         'notes.html', {
#             'request': request,
#             'title': 'Notes',
#             'notes': notes,
#             'tags': tags,
#             'authenticated_username': authenticated_username,
#         },
#     )
