from http import HTTPStatus
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


def test_get_tags(client, create_tags):
    # test default json works
    r = client.get('/tags/')
    assert r.ok
    assert [tag['name'] for tag in r.json()] == ['books', 'archive', 'groceries']

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
    assert r.json() == {"tag dont exists": 'notexists'}, r.json()


def test_delete_tag(client, create_user):
    r = client.post('/tags/', json={'name': 'tag_to_be_removed', 'color': '#ffaace'})
    assert r.ok
    r = client.post('/users/test_user/notes/', json={"text": 'fake_text', "tags": ['tag_to_be_removed']})
    assert r.ok
    note_id = r.json()['id']
    assert client.delete(f'/tags/tag_to_be_removed').ok
    assert 'tag_to_be_removed' not in client.get(f'/notes/{note_id}').json()['tags']
