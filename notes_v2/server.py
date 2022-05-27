from notes_v2 import schemas

import operator
from http import HTTPStatus

import secrets
import markdown2

from fastapi import Depends, FastAPI, HTTPException, status, Header, Request, Form, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from notes import crud, models, schemas, util
from notes.database import SessionLocal, engine

CSS_FRAMEWORK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css"/>'

markdowner = markdown2.Markdown(extras=[
    'fenced-code-blocks',
    'code-friendly',  # https://github.com/trentm/python-markdown2/issues/38
])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


# @app.post('/notes/', response_model=schemas.Note)
# def create_note(username: str, note: schemas.NoteCreate, db: Session = Depends(get_db)):
#     # try:
#     #     res = crud.create_note(db, note, username)
#     # except crud.TagNotExistsError as e:
#     #     raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"tags dont exists": e.args[0]})
#     # return res
