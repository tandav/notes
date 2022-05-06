from fastapi import Depends, FastAPI, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from http import HTTPStatus

from notes import crud
from notes import models
from notes import schemas
from notes.database import SessionLocal, engine
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{username}/notes/", response_model=schemas.Note)
def create_note(
    username: str, note: schemas.NoteCreate, db: Session = Depends(get_db)
):
    try:
        res = crud.create_note(db, note, username)
    except crud.TagNotExistsError as e:
        raise HTTPException(status_code=400, detail={"tags dont exists": e.args[0]})
    return res


@app.post('/tags/', response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = crud.get_tag_by_name(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=400, detail=f"tag with name {tag.name} username already exists")
    return crud.create_tag(db, tag)


@app.get('/tags/', response_model=list[schemas.Tag])
def read_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db)


@app.get("/notes/", response_model=list[schemas.Note])
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_notes(db, skip=skip, limit=limit)


@app.delete("/notes/{note_id}", response_model=list[schemas.Note])
def delete_note(note_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_note(db, note_id)
    except crud.NoteNotExistsError:
        raise HTTPException(status_code=400, detail={"note dont exists": note_id})


@app.get('/', response_class=HTMLResponse)
def root():
    return """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css">
    <h1>create note</h1>
    <form action="/signup" method="post">
      <p>
        <label><input type="checkbox" value="is_bookmark">bookmark</label>
        <label><input type="checkbox" value="is_private">private</label>
      </p>

      <p>
        <label>title</label><br>
        <input type="text" name="title">
      </p>
      <p>
        <label for="textarea">text or url</label>
        <textarea id="textarea" rows="8" cols="48" placeholder="Enter your message here"></textarea>
      </p>
      <p>
        <label>tags</label><br>
          <p>
            <label><input type="checkbox" value="is_bookmark">bookmark</label>
            <label><input type="checkbox" value="is_private">private</label>
          </p>
      </p>
      <p>
        <button>create</button>
      </p>
    </form>
    <style>
    input[name=title] {
        width: 440px;
    }
    </style>
    """


#     db.insert(text)
#     print(text)
#     return RedirectResponse('/', status_code=HTTPStatus.FOUND)
#


# from fastapi import FastAPI
# from fastapi import Form
# from fastapi.responses import HTMLResponse
# import starlette.status as status
#
# from database import Database
# import util
#
#
# db = Database('notes.db')
# app = FastAPI()
#
# header = '''\
# <span class='header'>
# <a class='link' href='/'>HOME</a>
# <a class='link' href='/create'>NEW NOTE</a>
# </span>
# '''
#
# css = '''
# <style>
# .header .link {
#     margin-right: 20px;
# }
# body {
#     background-color: rgba(0,0,0, 0.04);
#     font-family: monospace;
#
# }
# .note {
#     padding: 10px;
#     border: 1px solid rgba(0,0,0,0.5);
#     box-shadow: 2px 2px;
#     border-radius: 3px;
#     background: white;
# }
# #text {
#     height: 75px;
#     font-family: monospace;
#     margin-bottom: 20px;
# }
#
# /* mobile */
# @media screen and (max-width: 1080px) {
#     body {
#         font-size: 2em;
#     }
#     #text {
#         width: 100%;
#     }
#
# }
#
# /* desktop */
# @media screen and (min-width: 1080px) {
#     body {
#         margin: auto;
#         width: 500px;
#     }
#     #text {
#         width: 500px;
#     }
# }
# </style>
# '''
#
#
# @app.get('/', response_class=HTMLResponse)
# async def root():
#     html = ''.join(f'''
#     <pre class='note'>
#     {{'id': {i}, 'timestamp': '{util.ago(t)}'}}
#     ----------------------------------------------------
#     {text}
#     </pre>
#     '''
#     for i, t, text in db.get_all()
#     )
#     return header + html + css
#
# @app.get('/create', response_class=HTMLResponse)
# async def create():
#     html = '''
#     <h1/>create note<h1>
#     <form action='/note', method='post'>
#         <input type="text" id="text" name="text">
#         <input type="submit" value="create">
#     </form>
#     '''
#     return header + html + css
#
#
# @app.post('/note')
# async def save_note(text: str = Form(...)):
#     db.insert(text)
#     print(text)
#     return RedirectResponse('/', status_code=status.HTTP_302_FOUND)
