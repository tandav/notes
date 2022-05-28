from http import HTTPStatus
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, Header
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from notes_v2 import crud
from notes_v2 import schemas
from notes_v2.util import MediaType
from notes_v2.util import header
from notes_v2.dependencies import get_db
from notes_v2.dependencies import http_basic
from notes_v2.dependencies import http_basic_optional


# TODO: maybe set prefix /users here is a good idea
# https://fastapi.tiangolo.com/tutorial/bigger-applications/?h=files#another-module-with-apirouter
router = APIRouter(
    tags=['users'],
)


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
    responses={
        200: {
            "content": {"text/html": {}},
            "description": "return users as JSON list or as HTML table",
        },
        415: {"model": schemas.Message},
    }
)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), accept=Header(default='application/json')):
    mediatype = MediaType(accept)
    if mediatype.is_unsupported:
        raise MediaType.UNSUPPORTED_EXCEPTION
    users = crud.user.read_many(db, skip=skip, limit=limit)
    if mediatype.is_json:
        return users
    rows = '\n'.join(
        f'''
        <tr>
            <td><a href='/notes/{note['id']}'>{note['id']}</a></td>
            <td>{note['text'] or ''}</td>
            <td>{util.format_url(note['url'])}</td>
            <td>{','.join(f'<a href="/tags/{tag}">{tag}</a>' for tag in note['tags'])}</td>
            <td title="{util.format_time(note['updated_time'], absolute=True)}">{util.format_time(note['updated_time'])}</td>
        </tr>
        '''
        for note in notes
    )

    html = f'''
    <table>
    <thead>
        <tr>
            <th>id</th>
            <th>text</th>
            <th>url</th>
            <th>tags</th>
            <th>last edit</th>
        </tr>
    </thead>
    <tbody>
    {rows}
    </tbody>
    </table>
    '''
    return HTMLResponse(header())


@router.get("/users/{username}", response_model=schemas.User)
def read_user_by_name(username: str, db: Session = Depends(get_db)):
    db_user = crud.user.read_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return db_user
