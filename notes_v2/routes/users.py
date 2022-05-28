from http import HTTPStatus
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, Header
from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from notes_v2 import crud
from notes_v2 import schemas
# from notes_v2.util import header
from notes_v2.dependencies import get_db
from notes_v2.dependencies import guess_type
from notes_v2.dependencies import http_basic
from notes_v2.dependencies import http_basic_optional


# TODO: maybe set prefix /users here is a good idea
# https://fastapi.tiangolo.com/tutorial/bigger-applications/?h=files#another-module-with-apirouter
router = APIRouter(
    tags=['users'],
)

templates = Jinja2Templates(directory="notes_v2/templates")


@router.post("/users/", response_model=schemas.User)
def create_user(credentials: HTTPBasicCredentials = Depends(http_basic), db: Session = Depends(get_db)):
    """Create a user using username and password
    if user already exists returns an error
    """
    db_user = crud.user.read_by_username(db, username=credentials.username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="username already registered")
    return crud.user.create(db=db, user=credentials)


@router.get(
    "/users/",
    response_model=list[schemas.User],
    responses={200: {"content": {"text/html": {}}}}
)
def read_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    mediatype = Depends(guess_type),
):
    users = crud.user.read_many(db, skip=skip, limit=limit)
    if mediatype == 'json':
        return users
    # rows = '\n'.join(
    #     f'''
    #     <tr>
    #         <td><a href='/notes/{note['id']}'>{note['id']}</a></td>
    #         <td>{note['text'] or ''}</td>
    #         <td>{util.format_url(note['url'])}</td>
    #         <td>{','.join(f'<a href="/tags/{tag}">{tag}</a>' for tag in note['tags'])}</td>
    #         <td title="{util.format_time(note['updated_time'], absolute=True)}">{util.format_time(note['updated_time'])}</td>
    #     </tr>
    #     '''
    #     for note in notes
    # )
    #
    # html = f'''
    # <table>
    # <thead>
    #     <tr>
    #         <th>id</th>
    #         <th>text</th>
    #         <th>url</th>
    #         <th>tags</th>
    #         <th>last edit</th>
    #     </tr>
    # </thead>
    # <tbody>
    # {rows}
    # </tbody>
    # </table>
    # '''
    # return HTMLResponse(header())
    # return HTMLResponse('hello')
    users = [schemas.User.from_orm(u) for u in users]
    return templates.TemplateResponse('users.html', {
        'request': request,
        'users': users,
    })


@router.get(
    "/users/{username}",
    response_model=schemas.User,
    responses={200: {"content": {"text/html": {}}}}
)
def read_user_by_name(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
):
    db_user = crud.user.read_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    if mediatype == 'json':
        return db_user
    # return templates.TemplateResponse('user.html', {
    #     "request": request, "id": db_user.id,
    #     'username': db_user.username,
    # })
    # breakpoint()
    user = schemas.User.from_orm(db_user).dict()
    return templates.TemplateResponse('user.html', {"request": request, **user})
