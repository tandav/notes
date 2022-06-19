from http import HTTPStatus
from notes import crud
from notes.util import is_hex_color
from xml.etree import ElementTree


def test_create_tags(client):
    r = client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
    assert r.ok

    r = client.post('/tags/', json={'name': 'archive', 'color': '#f0ffff'})
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

    # test valid characters
    for name in ('fdf&', 'ffdf dfs', '!'):
        r = client.post('/tags/', json={'name': name, 'color': '#c0ffee'})
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert r.json() == {'detail': [{'loc': ['body', 'name'], 'msg': 'tag name can only contain letters, digints and "_", "-" special characters', 'type': 'value_error'}]}

    # test startswith letter
    for name in ('1name', '_', '_t', '-', '-4'):
        r = client.post('/tags/', json={'name': name, 'color': '#c0ffee'})
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert r.json() == {'detail': [{'loc': ['body', 'name'], 'msg': 'tag name should must start with a letter', 'type': 'value_error'}]}


def test_get_tags(client, create_tags):
    # test default json works
    r = client.get('/tags/')
    assert r.ok
    assert [tag['name'] for tag in r.json()] == ['groceries', 'archive', 'books']

    # test sorted by updated_time
    assert r.json() == sorted(r.json(), key=lambda x: x['updated_time'], reverse=True)

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


def test_get_tag(client, create_tags):
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
    assert r.json() == {'tag dont exists': 'notexists'}, r.json()


def test_delete_tag(client, create_user):
    r = client.post('/tags/', json={'name': 'tag_to_be_removed', 'color': '#ffaace'})
    assert r.ok
    r = client.post('/users/test_user/notes/', json={'text': 'fake_text', 'tags': ['tag_to_be_removed']})
    assert r.ok
    note_id = r.json()['id']
    assert client.delete(f'/tags/tag_to_be_removed').ok
    assert 'tag_to_be_removed' not in client.get(f'/notes/{note_id}').json()['tags']


def test_updated_time(client, create_user, create_tags):
    """Tag.updated_time should updates when you create or modify a note with this tag"""
    t0 = client.get('/tags/books').json()['updated_time']

    note_id = client.post('/users/test_user/notes/', json={'text': None, 'url': None, 'tags': ['books']}).json()['id']
    t1 = client.get('/tags/books').json()['updated_time']

    assert t1 > t0
    client.post(f'/notes/{note_id}/edit/', json={'text': '1', 'tags': ['books', 'groceries']})
    t2 = client.get('/tags/books').json()['updated_time']

    assert t2 > t1
