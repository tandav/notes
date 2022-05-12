import pytest
from http import HTTPStatus
from notes import models
from faker import Faker
from xml.etree import ElementTree
from notes.util import is_hex_color
fake = Faker()


@pytest.mark.parametrize('table', [
    models.User,
    models.Note,
    models.Tag,
    # models.Attachment,
])
def test_tables_empty(db, table):
    assert db.query(table).count() == 0


def test_create_user(client):
    response = client.post("/users/", json={"username": "test_user", "password": "test_password"})
    assert response.ok, response.json()
    j = response.json()
    assert j.pop('created_time')
    assert j.pop('updated_time')
    assert j == {
        'id': 1,
        'username': 'test_user',
    }

    # create more users
    for _ in range(2):
        username = fake.user_name()
        password = fake.password(length=32, special_chars=False)
        assert client.post("/users/", json={"username": username, "password": password}).ok


def test_username_already_registred(client):
    response = client.post(
        "/users/",
        json={"username": "test_user", "password": "test_password"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'username already registered'}


def test_create_note(client):
    for _ in range(3):
        r = client.post('/users/test_user/notes/', json={
            "text": fake.text(max_nb_chars=200),
            "url": fake.uri(),
            "tags": [],
        })
        assert r.ok, r.json()

    # test url validation
    r = client.post('/users/test_user/notes/', json={"url": "ff", "tags": []})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json() == {'detail': [{'loc': ['body', 'url'], 'msg': 'url must starts with http', 'type': 'value_error'}]}

    r = client.post('/users/test_user/notes/', json={"url": "https://example.com?q=hello world", "tags": []})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json() == {'detail': [{'loc': ['body', 'url'], 'msg': 'url cant contain spaces', 'type': 'value_error'}]}


def test_create_tags(client):
    r = client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
    assert r.ok

    # test already created
    r = client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json() == {'detail': 'tag with name books username already exists'}

    # test valid color generated
    r = client.post('/tags/', json={'name': 'groceries'})
    assert is_hex_color(r.json()['color'])

    r = client.post('/tags/', json={'name': 'fake', 'color': 'bad-color'})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # test empty name raises
    r = client.post('/tags/', json={'name': '', 'color': '#c0ffee'})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json() == {'detail': [{'loc': ['body', 'name'], 'msg': 'tag name cant be empty', 'type': 'value_error'}]}


def test_get_tags(client):
    # test default json works
    r = client.get('/tags/')
    assert r.ok
    assert [tag['name'] for tag in r.json()] == ['books', 'groceries']

    # test json
    assert client.get('/tags/', headers={'Accept': 'application/json'}).ok

    # test html
    r = client.get('/tags/', headers={'Accept': 'text/html'})
    assert r.ok
    assert r.text
    ElementTree.fromstring(r.text)

    # test unsupported media type
    r = client.get('/tags', headers={'Accept': 'image/png'})
    assert r.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert r.json() == {'detail': '415 Unsupported Media Type'}


def test_create_note_with_tags(client):
    # 1 tag
    r = client.post('/users/test_user/notes/', json={
        "text": fake.text(max_nb_chars=200),
        "url": fake.uri(),
        "tags": ['books'],
    })
    assert r.ok

    # 2 tag
    r = client.post('/users/test_user/notes/', json={
        # "title": fake.text(max_nb_chars=30),
        "text": fake.text(max_nb_chars=200),
        "tags": ['books', 'groceries'],
    })
    assert r.ok

    # test error when tags does not exists
    r = client.post('/users/test_user/notes/', json={
        "text": fake.text(max_nb_chars=200),
        "url": fake.uri(),
        "tags": ['books', 'groceries', 'tag_does_not_exist'],
    })
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {"detail": {"tags dont exists": ['tag_does_not_exist']}}


def test_get_note(client):
    # test default json works
    r = client.get('/notes/1')
    assert r.ok
    assert r.json()['id'] == 1
    assert r.json()['user_id'] == 1
    assert r.json()['tags'] == []

    # test json
    assert client.get('/notes/1', headers={'Accept': 'application/json'}).ok

    # test html
    r = client.get('/notes/1', headers={'Accept': 'text/html'})
    assert r.ok
    assert r.text
    ElementTree.fromstring(r.text)

    # test unsupported media type
    r = client.get('/notes/1', headers={'Accept': 'image/png'})
    assert r.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # test note dont exists
    r = client.get('/notes/42')
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {"note dont exists": 42}, r.json()


def test_get_notes(client):
    # test default json works
    r = client.get('/notes')
    assert r.ok
    assert len(r.json()) == 5, r.json()

    # test json
    r = client.get('/notes', headers={'Accept': 'application/json'})
    assert r.ok
    assert len(r.json()) == 5, r.json()


    # test html
    r = client.get('/notes', headers={'Accept': 'text/html'})
    assert r.ok
    assert r.text
    ElementTree.fromstring(r.text)

    # test unsupported media type
    r = client.get('/notes', headers={'Accept': 'image/png'})
    assert r.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert r.json() == {'detail': '415 Unsupported Media Type'}


def test_get_tag(client):
    # test default json works
    r = client.get('/tags/books')
    assert r.ok
    assert r.json()['id'] == 1
    assert r.json()['name'] == 'books'
    assert r.json()['color'] == '#c0ffee'

    # test json
    assert client.get('/tags/books', headers={'Accept': 'application/json'}).ok

    # test html
    r = client.get('/tags/books', headers={'Accept': 'text/html'})
    assert r.ok
    assert r.text
    ElementTree.fromstring(r.text)

    # test unsupported media type
    r = client.get('/tags/books', headers={'Accept': 'image/png'})
    assert r.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # test tag dont exists
    r = client.get('/tags/notexists')
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {"tag dont exists": 'notexists'}, r.json()


def test_delete_note(client):
    r = client.delete('/notes/1')
    assert r.ok
    assert 1 not in {note['id'] for note in client.get('/notes').json()}

    r = client.delete('/notes/2')
    assert 2 not in {note['id'] for note in client.get('/notes').json()}


def test_get_tag_notes(client):
    r = client.get('/tags/books/notes')
    assert r.ok
    assert [note['id'] for note in r.json()] == [4, 5]

    r = client.get('/tags/groceries/notes')
    assert r.ok
    assert [note['id'] for note in r.json()] == [5]


def test_delete_tag(client):
    r = client.post('/tags/', json={'name': 'tag_to_be_removed', 'color': '#ffaace'})
    assert r.ok
    r = client.post('/users/test_user/notes/', json={"text": 'fake_text', "tags": ['tag_to_be_removed']})
    assert r.ok
    note_id = r.json()['id']
    assert client.delete(f'/tags/tag_to_be_removed').ok
    assert 'tag_to_be_removed' not in client.get(f'/notes/{note_id}').json()['tags']


def test_get_user_by_username(client):
    r = client.get('/users/test_user')
    assert r.ok
    assert r.json()['id'] == 1



@pytest.mark.parametrize('text', [None, 'test'])
@pytest.mark.parametrize('url', [None, 'https://test.com'])
@pytest.mark.parametrize('tags', [[], ['books']])
@pytest.mark.parametrize('edit_text', [None, 'edit_test'])
@pytest.mark.parametrize('edit_url', [None, 'https://edit.com'])
@pytest.mark.parametrize('edit_tags', [[], ['groceries'], ['books', 'groceries']])
def test_edit_note(client, text, url, tags, edit_text, edit_url, edit_tags):
    r = client.post('/users/test_user/notes/', json={"text": text, "url": url, "tags": tags})
    assert r.ok
    initial = r.json()

    r = client.post(f'/notes/{initial["id"]}/edit/', json={"text": edit_text, "url": edit_url, "tags": edit_tags})
    assert r.ok
    edited = r.json()

    assert edited['text'] == edit_text
    assert edited['url'] == edit_url
    assert edited['tags'] == edit_tags
    assert initial['created_time'] == edited['created_time'], str(initial)
    assert initial['updated_time'] < edited['updated_time'], str(initial)


def test_edit_note_not_exists(client):
    # test error raised when try to edit non-existing note
    r = client.post('/notes/442/edit/', json={'text': 'test', 'tags': []})
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {'detail': {'note dont exists': 442}}

    # test error raised when try to use add tags which not exists
    r = client.post('/users/test_user/notes/', json={'text': 'test'})
    assert r.ok
    note_id = r.json()['id']
    r = client.post(f'/notes/{note_id}/edit/', json={'text': 'test', 'tags': ['books', 'unknown_tag']})
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {'detail': {'tags dont exists': ['unknown_tag']}}

