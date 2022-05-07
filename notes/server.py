from fastapi import Depends, FastAPI, HTTPException, Form, Header
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from http import HTTPStatus
from fastapi import Request

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


@app.get(
    "/notes/",
    response_model=list[schemas.Note],
    responses={
        200: {
            "content": {"text/html": {}},
            "description": "Return the html page with list of notes",
        },
        415: {"model": schemas.Message},
    }
)
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), accept=Header('application/json')):
    accept = accept.split(',')

    if accept[0] == 'text/html':
        return HTMLResponse('<h1>Notes</h1>')
    if 'application/json' in accept or '*/*' in accept:
        return crud.get_notes(db, skip=skip, limit=limit)
    else:
        return JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'message': '415 Unsupported Media Type'})



@app.delete("/notes/{note_id}", response_model=list[schemas.Note])
def delete_note(note_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_note(db, note_id)
    except crud.NoteNotExistsError:
        raise HTTPException(status_code=400, detail={"note dont exists": note_id})

@app.post('/new_note')
# async def save_note(text: str = Form(...), url):
async def new_note_handle_form(request: Request, db: Session = Depends(get_db)):

    form = await request.form()

    note = schemas.NoteCreate(
        text=form.get('text') or None,
        url=form.get('url') or None,
        tags=form.getlist('tags'),
    )
    create_note(username='test_user', note=note, db=db)
    return RedirectResponse('/', status_code=HTTPStatus.FOUND)


@app.get('/new_note', response_class=HTMLResponse)
def new_note_form(db: Session = Depends(get_db)):
    tags = crud.get_tags(db)
    tags_checkboxes = '\n'.join(
        # f'<label class="tag" id="{tag.name}"><input type="checkbox" name="{tag.name}" value="{tag.name}">{tag.name}</label>'
        f'<label class="tag" id="{tag.name}"><input type="checkbox" name="tags" value="{tag.name}">{tag.name}</label>'
        # f'<label class="tag" id="{tag.name}"><input type="checkbox" name="{tag.name}">{tag.name}</label>'
        for tag in tags
    )
    # colors = {tag.name}

    html = f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css">
    <a href="/notes">[notes]</a>
    <a href="/tags">[tags]</a>
    <a href="/new_tag"><button>new tag</button></a>
    <h1>create note</h1>
    <form action="/new_note" method="post" id="note_form">
      <p>
        <label for="textarea">text</label>
        <textarea type="input" rows="8" cols="48" placeholder="Enter your note here" form="note_form" name="text"></textarea>
      </p>
      <p>
        <label>url</label><br>
        <input type="text" name="url">
      </p>
      <p>
        <label>tags</label><br>
          <p>
            {tags_checkboxes}
          </p>
      </p>
      <p>
        <button>create</button>
      </p>
    </form>
    """

    tags_colors = '\n'.join(f'''
    #{tag.name} {{
        background-color: {tag.color};
        padding: 0.25em;
        border-radius: 4px;
        margin: 3px;
    }}
    ''' for tag in tags)


    css = f'''
    <style>
    input[name=title] {{
        width: 440px;
    }}
    {tags_colors}
    </style>
    '''
    return html + css

@app.get('/', response_class=HTMLResponse)
def root(db: Session = Depends(get_db)):
    return RedirectResponse('/new_note')
# @app.get('/', response_class=HTMLResponse)
# def create_tag_page(db: Session = Depends(get_db)):
#     return

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
