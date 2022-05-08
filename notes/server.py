from fastapi import Depends, FastAPI, HTTPException, Form, Header
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from http import HTTPStatus
from fastapi import Request

from notes import crud
from notes import util
from notes import schemas
from notes.database import SessionLocal, engine
from fastapi.responses import JSONResponse

CSS_FRAMEWORK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css"/>'


app = FastAPI()


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
def read_user_by_name(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{username}/notes/", response_model=schemas.Note)
def create_note(username: str, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    try:
        res = crud.create_note(db, note, username)
    except crud.TagNotExistsError as e:
        raise HTTPException(status_code=404, detail={"tags dont exists": e.args[0]})
    return res


@app.post("/notes/{note_id}/edit/", response_model=schemas.Note)
def edit_note(note_id: int, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    try:
        res = crud.edit_note(db, note, note_id)
    except crud.NoteNotExistsError as e:
        raise HTTPException(status_code=404, detail={"note dont exists": e.args[0]})
    except crud.TagNotExistsError as e:
        raise HTTPException(status_code=404, detail={"tags dont exists": e.args[0]})
    return res


@app.post('/tags/', response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = crud.get_tag(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=400, detail=f"tag with name {tag.name} username already exists")
    return crud.create_tag(db, tag)


@app.get(
    "/tags/",
    response_model=list[schemas.Tag],
    responses={
        200: {
            "content": {"text/html": {}},
            "description": "Return the html page with list of notes",
        },
        415: {"model": schemas.Message},
    }
)
def read_tags(db: Session = Depends(get_db), accept=Header('application/json')):
    accept = accept.split(',')
    is_html = accept[0] == 'text/html'
    is_json = 'application/json' in accept or '*/*' in accept
    if is_html or is_json:
        tags = crud.get_tags(db)
        if is_json:
            return tags
        if is_html:
            rows = '\n'.join(
                f'''
                  <tr>
                      <td>{tag.id}</td>
                      <td><a href='/tags/{tag.name}'>{tag.name}</a></td>
                      <td id="{tag.name}">{tag.color}</td>
                      <td title="{util.format_time(tag.updated_time, absolute=True)}">{util.format_time(tag.updated_time)}</td>
                  </tr>
                  '''
                for tag in tags
            )
            tags_colors = util.tags_css(tags)
            # f'<a href="/tags/{tag.name}"><label class="tag" id="{tag.name}">{tag.name}</label></a>'
            return HTMLResponse(f'''
            <html>
            <head>
            {CSS_FRAMEWORK}
            </head>
            <body>
            {util.header(new_tag=True)}
            <h1>Tags</h1>
            <table>
            <thead>
                <tr>
                    <th>id</th>
                    <th>name</th>
                    <th>color</th>
                    <th>last edit</th>
                </tr>
            </thead>
            <tbody>
            {rows}
            </tbody>
            </table>
            <style>
            {tags_colors}
            </style>
            </body>
            </html>
            ''')
    else:
        return JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'detail': '415 Unsupported Media Type'})


def notes_table(notes: list) -> tuple[str, str]:
    rows = '\n'.join(
        f'''
        <tr>
            <td><a href='/notes/{note['id']}'>{note['id']}</a></td>
            <td><a href='/users/{note['user_id']}'>{note['user_id']}</a></td>
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
            <th>user_id</th>
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

    css = '''
    td {
        max-width:100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    '''

    return html, css


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
    is_html = accept[0] == 'text/html'
    is_json = 'application/json' in accept or '*/*' in accept

    if is_html or is_json:
        notes = crud.get_notes(db, skip=skip, limit=limit)
        if is_json:
            return notes
        if is_html:
            table_html, table_css = notes_table(notes)
            return HTMLResponse(f'''
            <html>
            <head>
            {CSS_FRAMEWORK}
            </head>
            <body>
            <nav>
            {util.header(new_note=True)}
            </nav>
            <h1>Notes</h1>
            {table_html}
            ''' + f'''
            <style>
            {table_css}
            </style>
            </body>
            </html>
            ''')

    else:
        return JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'detail': '415 Unsupported Media Type'})


@app.get(
    "/notes/{note_id}",
    response_model=schemas.Note,
    responses={
        200: {
            "content": {"text/html": {}},
            "description": "Return the html page with note",
        },
        415: {"model": schemas.Message},
        404: {"model": schemas.Message},
    }
)
def get_note(note_id: int, db: Session = Depends(get_db), accept=Header('application/json')):
    accept = accept.split(',')
    is_html = accept[0] == 'text/html'
    is_json = 'application/json' in accept or '*/*' in accept
    if is_html or is_json:
        try:
            note = crud.get_note(db, note_id)
        except crud.NoteNotExistsError:
            return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"note dont exists": note_id})
        else:
            if is_html:
                tags = '\n'.join(
                    f'<a href="/tags/{tag.name}"><label class="tag" id="{tag.name}">{tag.name}</label></a>'
                    for tag in note.tags
                )
                tags_colors = util.tags_css(note.tags)

                url = f"<p>url: <a href='{note.url}'>{note.url}</a></p>" if note.url else ''
                text = f"<p>{note.text}</p>" if note.text else ''
                return HTMLResponse(f'''
                <html>
                <head>
                {CSS_FRAMEWORK}
                </head>
                ''' + '''
                <body>
                <script>
                const delete_note = note_id => {
                    if (confirm('delete confirmation')) {
                        fetch(`/notes/${note_id}`, {method: 'DELETE'})
                        window.location = "/notes"
                    }
                }
                </script>
                ''' + f'''
                <header>
                <nav>
                {util.header(new_note=True, edit_note=note_id)}
                <button class="delete_button" onclick='delete_note({note_id})'>delete</button>
                </nav>
                <span class='metadata'><a href='/users/{note.user_id}'>user_{note.user_id}</a> last edit: {note.updated_time:%Y %b %d %H:%M}</span>
                </header>
                {url}
                <p></p>
                <div class='tags'>
                {tags}
                </div>
                <hr/>
                {text}
                ''' + f'''
                <style>
                .delete_button {{
                    background-color: #EF5350;
                }}
                {tags_colors}

  
                header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                </style>
                </body>
                </html>
                ''')
            if is_json:
                return note
    else:
        return JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'message': '415 Unsupported Media Type'})


@app.get('/tags/{name}/notes')
def get_tag_notes(name: str, db: Session = Depends(get_db)):
    return crud.get_tag(db, name).notes


@app.get(
    "/tags/{name}",
    response_model=schemas.Tag,
    responses={
        200: {
            "content": {"text/html": {}},
            "description": "Return the html page with note",
        },
        415: {"model": schemas.Message},
        404: {"model": schemas.Message},
    }
)
def get_tag(name: str, db: Session = Depends(get_db), accept=Header('application/json')):
    accept = accept.split(',')
    is_html = accept[0] == 'text/html'
    is_json = 'application/json' in accept or '*/*' in accept
    if is_html or is_json:
        tag = crud.get_tag(db, name)
        if tag is None:
            return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"tag dont exists": name})
        if is_json:
            return tag
        if is_html:
            tags_colors = util.tags_css([tag])

            table_html, table_css = notes_table([note.to_dict() for note in tag.notes])
            return HTMLResponse(f'''
            <html>
            <head>
            {CSS_FRAMEWORK}
            </head>
            <body>
            ''' + '''
            <script>
            const delete_tag = name => {
                if (confirm('delete confirmation')) {
                    fetch(`/tags/${name}`, {method: 'DELETE'})
                    window.location = "/tags"
                }
            }
            </script>
            ''' + f'''
            <header>
            <nav>
            {util.header(new_tag=True)}
            <button class="delete_button" onclick='delete_tag("{name}")'>delete</button>
            </nav>
            <span class='metadata'>last edit: {tag.updated_time:%Y %b %d %H:%M}</span>
            </header>
            <h1><span>{tag.name}</span></h1>
            {table_html}
            ''' + f'''
            <style>
            .delete_button {{
                background-color: #EF5350;
            }}
            {tags_colors}
            header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            h1 span {{
                background-color: {tag.color};
                padding: 0.25em;
                border-radius: 4px;
            }}
            {table_css}
            </style>
            </body>
            </html>
            ''')
    else:
        return JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'message': '415 Unsupported Media Type'})


@app.delete("/notes/{note_id}", response_model=list[schemas.Note])
def delete_note(note_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_note(db, note_id)
    except crud.NoteNotExistsError:
        raise HTTPException(status_code=404, detail={"note dont exists": note_id})


@app.delete("/tags/{name}", response_model=list[schemas.Tag])
def delete_tag(name: str, db: Session = Depends(get_db)):
    try:
        crud.delete_tag(db, name)
    except crud.NoteNotExistsError:
        raise HTTPException(status_code=404, detail={"note dont exists": name})


@app.post('/new_note')
async def new_note_handle_form(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    note = schemas.NoteCreate(
        text=form.get('text') or None,
        url=form.get('url') or None,
        tags=form.getlist('tags'),
    )
    create_note(username='test_user', note=note, db=db)
    return RedirectResponse('/notes', status_code=HTTPStatus.FOUND)


@app.post('/notes/{note_id}/edit')
async def edit_note_handle_form(note_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    note = schemas.NoteCreate(
        text=form.get('text') or None,
        url=form.get('url') or None,
        tags=form.getlist('tags'),
    )
    edit_note(note_id, note, db)
    return RedirectResponse('/notes', status_code=HTTPStatus.FOUND)


@app.post('/new_tag')
async def new_tag_handle_form(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    tag = schemas.TagCreate(
        name=form['name'],
        color=form.get('color') or None,
    )
    create_tag(tag=tag, db=db)
    return RedirectResponse('/tags', status_code=HTTPStatus.FOUND)


def note_form(db: Session, action: str, note_id: int | None = None):
    if action == 'new_note':
        button_text = 'create'
        text = ''
        url = ''
        form_action = '/new_note'
    elif action == 'edit_note':
        assert note_id is not None
        note = crud.get_note(db, note_id)
        text = note.text
        url = note.url
        button_text = 'save'
        form_action = f'/notes/{note_id}/edit'
    else:
        raise ValueError


    tags = crud.get_tags(db)
    tags_checkboxes = []
    for tag in crud.get_tags(db):
        checked = ' checked' if action == 'edit_note' and tag in note.tags else ''
        # {"" if action == "edit_note" and tag.name in note_tags}
        s = f'<label class="tag" id="{tag.name}"><input type="checkbox" name="tags" value="{tag.name}"{checked}>{tag.name}</label>'
        tags_checkboxes.append(s)
    tags_checkboxes = '\n'.join(tags_checkboxes)

    html = f"""
    {CSS_FRAMEWORK}
    {util.header(new_note=False)}
    <h1>create note</h1>
    <form action="{form_action}" method="post" id="note_form">
      <p>
        <label for="textarea">text</label>
        <textarea type="input" placeholder="Enter your note here" form="note_form" name="text">{text}</textarea>
      </p>
      <p>
        <label>url (optional)</label><br>
        <input type="text" name="url"{url}>
      </p>
      <p>
        <label>tags</label><br>
          <p>
            {tags_checkboxes}
          </p>
      </p>
      <p>
        <button>{button_text}</button>
      </p>
    </form>
    """

    tags_colors = util.tags_css(tags)

    css = f'''
    <style>
    input[name=url] {{
        width: 100%;
    }}

    textarea {{
        font-family: monospace;
        font-size: 9pt;
    }}

    {tags_colors}
    </style>
    '''
    return html + css


@app.get('/new_note', response_class=HTMLResponse)
def new_note_form(db: Session = Depends(get_db)):
    return note_form(db, action='new_note')


@app.get('/notes/{note_id}/edit', response_class=HTMLResponse)
def edit_note_form(note_id: int, db: Session = Depends(get_db)):
    return note_form(db, action='edit_note', note_id=note_id)


@app.get('/new_tag', response_class=HTMLResponse)
def new_tag_form():
    html = f'''
    {CSS_FRAMEWORK}
    {util.header()}
    <h1>create tag</h1>
    <form action="/new_tag" method="post" id="tag_form">
      <p>
        <label>name</label>
        <input type="text" name="name">
      </p>
      <p>
        <label>color</label>
        <input type="color" name="color">
      </p>
      </p>
      <p>
        <button>create</button>
      </p>
    </form>
    '''

    css = f'''
    <style>
    input[name=name] {{
        width: 100%;
    }}
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
