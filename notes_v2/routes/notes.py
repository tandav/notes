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
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import notes_v2.crud.note
from notes_v2 import crud
from notes_v2 import models
from notes_v2 import schemas
from notes_v2 import util

# from notes_v2.util import header
from notes_v2.dependencies import authenticate_optional
from notes_v2.dependencies import get_db
from notes_v2.dependencies import guess_type
from notes_v2.dependencies import http_basic
from notes_v2.dependencies import http_basic_optional
from notes_v2.templates import templates

router = APIRouter(
    tags=['notes'],
)


@router.post('/notes/', response_model=schemas.Note)
def create(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    return crud.note.create(db, note, authenticated_username)


# def note_form(
#     db: Session,
#     action: str,
#     note: schemas.NoteCreate | models.Note | None = None,
# ):
#     if action == 'new_note':
#         button_text = 'create'
#         heading = 'create note'
#         if note is not None and isinstance(note, schemas.NoteCreate):
#             text = note.text
#             url = note.url
#         else:
#             text = ''
#             url = ''
#         form_action = '/new_note'
#     elif action == 'edit_note':
#         heading = 'edit note'
#         # assert note_id is not None
#         # note = crud.get_note(db, note_id)
#         # text = note.text
#         # url = note.url
#         # button_text = 'save'
#         # form_action = f'/notes/{note_id}/edit'
#         assert note is not None and isinstance(note, models.Note)
#         text = note.text
#         url = note.url or ''
#         button_text = 'save'
#         form_action = f'/notes/{note.id}/edit'
#     else:
#         raise ValueError
#
#     tags = crud.get_tags(db)
#     tags_checkboxes = []
#     for tag in crud.get_tags(db):
#
#         if (
#             (isinstance(note, models.Note) and tag in note.tags) or
#             (isinstance(note, schemas.NoteCreate) and tag.name in note.tags) or
#             (action == 'new_note' and tag.name == 'private')
#         ):
#             checked = ' checked'
#         else:
#             checked = ''
#
#         # {"" if action == "edit_note" and tag.name in note_tags}
#         s = f'<label class="tag" id="{tag.name}"><input type="checkbox" name="tags" value="{tag.name}"{checked}>{tag.name}</label>'
#         tags_checkboxes.append(s)
#     tags_checkboxes = '\n'.join(tags_checkboxes)
#
#     html = f"""
#     {CSS_FRAMEWORK}
#     {util.header(new_note=False)}
#     <h1>{heading}</h1>
#     <form action="{form_action}" method="post" id="note_form">
#       <p>
#         <label for="textarea">text</label>
#         <textarea type="input" placeholder="Enter your note here" form="note_form" name="text">{text}</textarea>
#       </p>
#       <p>
#         <label>url (optional)</label><br>
#         <input type="url" name="url" value="{url}"/>
#       </p>
#       <p>
#         <label>tags</label><br>
#           <p>
#             {tags_checkboxes}
#           </p>
#       </p>
#       <p>
#         <button>{button_text}</button>
#       </p>
#     </form>
#     """
#
#     tags_colors = util.tags_css(tags)
#
#     css = f'''
#     <style>
#     input[name=url] {{
#         width: 100%;
#     }}
#
#     textarea {{
#         font-family: monospace;
#         font-size: 9pt;
#     }}
#
#     {tags_colors}
#     </style>
#     '''
#     return html + css


@router.post('/notes/new_note')
async def new_note_handle_form(
    request: Request,
    db: Session = Depends(get_db),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    form = await request.form()
    note = schemas.NoteCreate(
        text=form.get('text') or None,
        url=form.get('url') or None,
        tags=form.getlist('tags'),
    )
    note_db = create(note, db, authenticated_username)
    return RedirectResponse(f"/notes/{note_db['id']}", status_code=HTTPStatus.FOUND)


@router.get('/notes/create', response_class=HTMLResponse)
def create_form(
    request: Request,
    text: str | None = None,
    url: str | None = None,
    tags: str | None = None,
    db: Session = Depends(get_db),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    # breakpoint()
    if text or url or tags:
        tags = [] if tags is None else tags.split(',')
        try:
            note = schemas.NoteCreate(text=text, url=url, tags=tags)
        except ValueError as e:
            return str(e)
    else:
        note = None
    # return note_form(db, action='new_note', note=note)
    # return '<h1>create note form</h1>'
    return templates.TemplateResponse(
        'create_note_form.html', {
            'request': request,
            'form_action': 'new_note',
            'button_text': 'create',
            'text': '',
            'url': '',
            # 'notes': [schemas.Note.from_orm(u) for u in notes],
            'authenticated_username': authenticated_username,
        },
    )

@router.get(
    '/notes/',
    response_model=list[schemas.Note],
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
    notes = crud.note.read_many(db, skip=skip, limit=limit)

    if mediatype == 'json':
        return notes
    return templates.TemplateResponse(
        'notes.html', {
            'request': request,
            'notes': [schemas.Note(**n.to_dict()) for n in notes],
            'authenticated_username': authenticated_username,
        },
    )

@router.get(
    '/notes/{note_id}',
    response_model=schemas.Note,
    responses={200: {'content': {'text/html': {}}}},
)
def read(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    db_note = crud.note.read_by_id(db, note_id)
    if db_note is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Note not found')
    if mediatype == 'json':
        return db_note
    return templates.TemplateResponse(
        'note.html', {
            'request': request,
            'note': db_note.to_dict(),
            'authenticated_username': authenticated_username,
        },
    )