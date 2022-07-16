from http import HTTPStatus

import colortool
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import notes_v2.crud.exceptions
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
async def create(
    request: Request,
    # note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    if mediatype == 'json':
        payload = await request.json()
        try:
            note = schemas.NoteCreate(**payload)
        except crud.exceptions.CrudError as e:
            raise e.http
        except ValueError as e:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))

    elif mediatype == 'form':
        payload = await request.form()
        try:
            # note = schemas.NoteForm(**payload)
            # note = schemas.NoteCreate.parse_obj(note)
            note = schemas.NoteCreate(
                text=payload.get('text'),
                url=payload.get('url') or None,  # replace '' with None
                tag=payload.get('tag') or None,  # replace '' with None
                tags=payload.getlist('tags'),
                color=payload.get('color'),
                is_private=payload.get('is_private', False),
            )

        except crud.exceptions.CrudError as e:
            raise e.http
        except ValueError as e:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    try:
        db_note = crud.note.create(db, note, authenticated_username)
    except crud.exceptions.CrudError as e:
        raise e.http

    if mediatype == 'json':
        return db_note.to_dict()
    elif mediatype == 'form':
        return RedirectResponse(f'/notes/{db_note.id}', status_code=HTTPStatus.FOUND)
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)


@router.post(
    # '/notes/{note_id}/update',
    '/notes/{note_id}',
    response_model=schemas.Note,
    responses={200: {'content': {'text/html': {}}}},
)
async def update(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    if mediatype == 'json':
        payload = await request.json()
        try:
            note = schemas.NoteUpdate(**payload)
        except crud.exceptions.CrudError as e:
            raise e.http
        except ValueError as e:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    elif mediatype == 'form':
        payload = await request.form()
        try:
            # note = schemas.NoteForm(**payload)
            # note = schemas.NoteUpdate.parse_obj(note)

            note = schemas.NoteUpdate(
                text=payload.get('text'),
                url=payload.get('url') or None,  # replace '' with None
                tag=payload.get('tag') or None,  # replace '' with None
                tags=payload.getlist('tags'),
                color=payload.get('color'),
                is_private=payload.get('is_private', True),
            )
            # text: str | None = Form(None),
            # url: str | None = Form(None),
            # tags: list[str] = Form([]),
            # tag: str | None = Form(None),
            # color: str | None = Form(None),
            # is_private: bool = Form(False),
            # )
        except crud.exceptions.CrudError as e:
            raise e.http
        except ValueError as e:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    try:
        db_note = crud.note.update(note_id, note, db, authenticated_username)
    except crud.exceptions.CrudError as e:
        raise e.http

    if mediatype == 'json':
        return db_note.to_dict()
    elif mediatype == 'form':
        return RedirectResponse(f'/notes/{db_note.id}', status_code=HTTPStatus.FOUND)
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)


@router.get('/notes/create', response_class=HTMLResponse)
def create_form(
    request: Request,
    db: Session = Depends(get_db),
    authenticated_username: str | None = Depends(authenticate_optional),
    text: str | None = None,
    url: str | None = None,
    tags: str | None = None,
    tag_name: str | None = None,
    tag_color: str | None = None,
    is_private: bool = True,
):
    if text or url or tags:  # parse query params for update
        tags = [] if tags is None else tags.split(',')
        try:
            note = schemas.NoteCreate(
                text=text,
                url=url,
                tags=tags,
                tag=tag_name,
                color=tag_color,
                is_private=True,
            )
        except ValueError as e:
            return str(e)
    else:
        note = None

    return note_form(request, db, authenticated_username, note, action='create')


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

    db_note = db_note.to_dict()

    if mediatype == 'json':
        return db_note
    return templates.TemplateResponse(
        'note.html', {
            'request': request,
            'note': db_note,
            'note_edit': authenticated_username is not None,
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
    notes = [schemas.Note(**n.to_dict()) for n in crud.note.read_many(db, skip=skip, limit=limit)]
    # tags = [schemas.Note(**n.to_dict()) for n in crud.note.read_tags(db)]

    tags = []
    for tag in crud.note.read_tags(db):
        tag_ = tag.to_dict()
        font_color, border_color = colortool.font_border_colors(tag_['color'])
        tag_['color_pale'] = colortool.lighter(tag_['color'], ratio=0.8)
        tag_['font_color'] = font_color
        tags.append(tag_)

    if mediatype == 'json':
        return notes
    return templates.TemplateResponse(
        'notes.html', {
            'request': request,
            # 'notes': [schemas.Note(**n.to_dict()) for n in notes],
            'title': 'Notes',
            'notes': notes,
            'tags': tags,
            'authenticated_username': authenticated_username,
        },
    )


@router.get(
    '/tags/',
    response_model=list[schemas.Note],
    responses={200: {'content': {'text/html': {}}}},
)
def read_tags(
    request: Request,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):

    notes = [schemas.Note(**n.to_dict()) for n in crud.note.read_tags(db)]

    if mediatype == 'json':
        return notes

    return templates.TemplateResponse(
        'notes.html', {
            'request': request,
            # 'notes': [schemas.Note(**n.to_dict()) for n in notes],
            'notes': notes,
            'tags': notes,
            'title': 'Tags',
            'authenticated_username': authenticated_username,
        },
    )


@router.get(
    '/tags/{tag_name}',
    response_model=schemas.Note,
    responses={200: {'content': {'text/html': {}}}},
)
def read_tag(
    tag_name: str,
    request: Request,
    db: Session = Depends(get_db),
    mediatype=Depends(guess_type),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    tag_note = crud.note.read_by_tag(db, tag_name)

    if mediatype == 'json':
        return tag_note

    return templates.TemplateResponse(
        'note.html', {
            'request': request,
            'note': tag_note.to_dict(),
            'authenticated_username': authenticated_username,
        },
    )


def note_form(
    request: Request,
    db: Session,
    authenticated_username: str | None,
    note: schemas.NoteCreate | models.Note | None = None,
    action: str = 'create',
):
    if action == 'create':
        assert isinstance(note, schemas.NoteCreate) or note is None
        payload = {'text': '', 'url': '', 'heading': 'New note', 'action_url': '/notes/'}
    elif action == 'update':
        assert isinstance(note, models.Note)
        payload = {
            'text': note.text,
            'url': note.url,
            'tag': note.tag,
            'color': note.color,
            'is_private': note.is_private,
            'heading': 'Edit note',
            'action_url': f'/notes/{note.id}',
        }
    else:
        raise ValueError('action must be "create" or "update"')

    payload.update(request=request, action=action, authenticated_username=authenticated_username, is_private=True if note is None else note.is_private)

    tags = []
    for tag in crud.note.read_tags(db):
        tag_ = tag.to_dict()
        font_color, border_color = colortool.font_border_colors(tag_['color'])
        tag_['color_pale'] = colortool.lighter(tag_['color'], ratio=0.8)
        tag_['font_color'] = font_color
        if (
            (isinstance(note, models.Note) and tag in note.right_notes) or
            (isinstance(note, schemas.NoteCreate) and tag.name in note.tags)
            # (action == 'create' and tag.name == 'private')
        ):
            tag_['checked'] = True
        else:
            tag_['checked'] = False
        # s = f'<label class="tag" id="{tag.tag}"><input type="checkbox" name="tags" value="{tag.tag}"{checked}>{tag.tag}</label>'
        # tags_checkboxes.append(s)
        tags.append(tag_)
    # tags_checkboxes = '\n'.join(tags_checkboxes)
    payload['tags'] = tags
    return templates.TemplateResponse('note_form.html', payload)


@router.get('/notes/{note_id}/update', response_class=HTMLResponse)
def update_form(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    authenticated_username: str | None = Depends(authenticate_optional),
):
    db_note = crud.note.read_by_id(db, note_id)
    if db_note is None:
        raise crud.exceptions.NoteNotExistsError.http
    if db_note.user.username == 'anon':
        raise crud.exceptions.AnonNotesCantBeUpdated.http
    elif db_note.user.username != authenticated_username:
        raise crud.exceptions.UserIsNotAllowedToEditOtherUserNotes.http

    return note_form(request, db, authenticated_username, db_note, action='update')


# @router.post('/notes/{note_id}/update')
# async def update_form_handle(
#     request: Request,
#     note_id: int,
#     text: str | None = Form(None),
#     url: str | None = Form(None),
#     tags: list[str] = Form([]),
#     tag: str | None = Form(None),
#     color: str | None = Form(None),
#     is_private: bool = Form(False),
#     db: Session = Depends(get_db),
#     mediatype=Depends(guess_type),
#     authenticated_username: str | None = Depends(authenticate_optional),
# ):

    # note = schemas.NoteCreate(
    #     text=text,
    #     url=url,
    #     tags=tags,
    #     tag=tag,
    #     color=color,
    #     is_private=is_private,
    # )
    # try:
    #     note_db = crud.note.update(note_id, note, db, authenticated_username)
    # except crud.exceptions.CrudError as e:
    #     raise e.http
    # return RedirectResponse(f"/notes/{note_db['id']}", status_code=HTTPStatus.FOUND)
