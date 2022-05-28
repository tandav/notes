import markdown2

from fastapi import Depends, FastAPI, HTTPException, status, Header, Request, Form, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from notes_v2 import crud
from notes_v2 import models
from notes_v2 import schemas
from notes_v2 import util
from notes_v2.routes import users

CSS_FRAMEWORK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css"/>'

markdowner = markdown2.Markdown(extras=[
    'fenced-code-blocks',
    'code-friendly',  # https://github.com/trentm/python-markdown2/issues/38
])



app = FastAPI()
app.include_router(users.router)




# @app.post('/notes/', response_model=schemas.Note)
# def create_note(username: str, note: schemas.NoteCreate, db: Session = Depends(get_db)):
#     # try:
#     #     res = crud.create_note(db, note, username)
#     # except crud.TagNotExistsError as e:
#     #     raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"tags dont exists": e.args[0]})
#     # return res
