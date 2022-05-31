import markdown2
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Form
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import notes_v2.crud.user
from notes_v2 import config
from notes_v2 import crud
from notes_v2 import models
from notes_v2 import schemas
from notes_v2 import util
from notes_v2.dependencies import get_db
from notes_v2.dependencies import get_db_cm
from notes_v2.routes import nodes
from notes_v2.routes import users

CSS_FRAMEWORK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css"/>'

markdowner = markdown2.Markdown(
    extras=[
        'fenced-code-blocks',
        'code-friendly',  # https://github.com/trentm/python-markdown2/issues/38
    ],
)


app = FastAPI(
    title='Notes API',
    description=config.API_DESCRIPTION,
    contact={
        'name': 'Alexander Rodionov',
        'url': 'https://tandav.me',
        'email': 'tandav@tandav.me',
    },
)
app.include_router(users.router)
app.include_router(nodes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def create_anon_user_if_not_exists():
    with get_db_cm() as db:
        user = schemas.UserCreate(username=config.ANON_SERVICE_ACCOUNT_USERNAME, password=config.ANON_SERVICE_ACCOUNT_PASSWORD)
        db_user = crud.user.read_by_username(db, username=user.username)
        if db_user:
            return
        crud.user.create(db=db, user=user)


# @app.middleware('http')
# def determine_media_type(request: Request, call_next):
#     # mediatype = util.MediaType(request.headers['Accept'])
#     accept = request.headers.get('Accept')
#     if accept is None:
#         request.headers['Accept'] = 'application/json'
#     accept = request.headers.get['Accept'].split(',')
#
#     if mediatype.is_unsupported:
#         raise util.MediaType.UNSUPPORTED_EXCEPTION
#     response
#     response = await call_next(request)
#     response.headers["X-Process-Time"] = str(process_time)
#     return response


# @app.post('/notes/', response_model=schemas.Note)
# def create_note(username: str, note: schemas.NoteCreate, db: Session = Depends(get_db)):
#     # try:
#     #     res = crud.create_note(db, note, username)
#     # except crud.TagNotExistsError as e:
#     #     raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"tags dont exists": e.args[0]})
#     # return res

@app.get('/')
def root():
    return RedirectResponse('/users/')
