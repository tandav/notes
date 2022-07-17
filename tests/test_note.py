import pytest
from http import HTTPStatus
from xml.etree import ElementTree


def test_create_note(client, fake, create_user):
    for _ in range(3):
        r = client.post(
            '/users/test_user/notes/', json={
                'text': fake.text(max_nb_chars=200),
                'url': fake.uri(),
                'tags': [],
            },
        )
        assert r.ok, r.json()

    # test url validation
    r = client.post('/users/test_user/notes/', json={'url': 'ff', 'tags': []})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json() == {'detail': [{'loc': ['body', 'url'], 'msg': 'url must starts with http', 'type': 'value_error'}]}

    r = client.post('/users/test_user/notes/', json={'url': 'https://example.com?q=hello world', 'tags': []})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json() == {'detail': [{'loc': ['body', 'url'], 'msg': 'url cant contain spaces', 'type': 'value_error'}]}


def test_create_note_with_tags(client, fake, create_user, create_tags):
    # 1 tag
    r = client.post(
        '/users/test_user/notes/', json={
            'text': fake.text(max_nb_chars=200),
            'url': fake.uri(),
            'tags': ['books'],
        },
    )
    assert r.ok

    r = client.post(
        '/users/test_user/notes/', json={
            'text': fake.text(max_nb_chars=200),
            'url': fake.uri(),
            'tags': ['archive'],
        },
    )
    assert r.ok

    # 2 tag
    r = client.post(
        '/users/test_user/notes/', json={
            # "title": fake.text(max_nb_chars=30),
            'text': fake.text(max_nb_chars=200),
            'tags': ['books', 'groceries'],
        },
    )
    assert r.ok

    # test error when tags does not exists
    r = client.post(
        '/users/test_user/notes/', json={
            'text': fake.text(max_nb_chars=200),
            'url': fake.uri(),
            'tags': ['books', 'groceries', 'tag_does_not_exist'],
        },
    )
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {'detail': {'tags dont exists': ['tag_does_not_exist']}}


def test_get_note(client, fake, create_user, create_tags):
    r = client.post(
        '/users/test_user/notes/', json={
            'text': fake.text(max_nb_chars=200),
            'url': fake.uri(),
            'tags': [],
        },
    )

    # ==== note without tags ====
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

    # ==== note with tags ====
    r = client.post(
        '/users/test_user/notes/', json={
            'text': fake.text(max_nb_chars=200),
            'tags': ['books', 'groceries'],
        },
    )
    note_id = r.json()['id']
    # test default json works
    r = client.get(f'/notes/{note_id}')
    assert r.ok
    assert r.json()['tags'] == ['books', 'groceries']

    # test json
    assert client.get(f'/notes/{note_id}', headers={'Accept': 'application/json'}).ok

    # test html
    r = client.get(f'/notes/{note_id}', headers={'Accept': 'text/html'})
    assert r.ok
    assert r.text
    ElementTree.fromstring(r.text)

    # test unsupported media type
    r = client.get(f'/notes/{note_id}', headers={'Accept': 'image/png'})
    assert r.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # ==== test note dont exists ====
    r = client.get('/notes/42')
    assert r.status_code == HTTPStatus.NOT_FOUND
    assert r.json() == {'note dont exists': 42}, r.json()


def test_get_notes(client, fake, create_user, create_tags):
    for _ in range(6):
        client.post('/users/test_user/notes/', json={'text': fake.text(max_nb_chars=200), 'tags': []})

    # test default json works
    r = client.get('/notes')
    assert r.ok
    assert len(r.json()) == 6, r.json()

    # test sorted by updated_time
    assert r.json() == sorted(r.json(), key=lambda x: x['updated_time'], reverse=True)

    # test json
    r = client.get('/notes', headers={'Accept': 'application/json'})
    assert r.ok
    assert len(r.json()) == 6, r.json()

    # test html
    r = client.get('/notes', headers={'Accept': 'text/html'})
    assert r.ok
    assert r.text
    ElementTree.fromstring(r.text)

    # test unsupported media type
    r = client.get('/notes', headers={'Accept': 'image/png'})
    assert r.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert r.json() == {'detail': '415 Unsupported Media Type'}

    # test archived notes are not returned
    r = client.get('/notes')
    assert r.ok
    for note in r.json():
        assert 'archive' not in note['tags']


def test_delete_note(client, fake, create_user):
    client.post('/users/test_user/notes/', json={'text': fake.text(max_nb_chars=200), 'tags': []})

    r = client.delete('/notes/1')
    assert r.ok
    assert 1 not in {note['id'] for note in client.get('/notes').json()}

    r = client.delete('/notes/2')
    assert 2 not in {note['id'] for note in client.get('/notes').json()}


def test_archive_note(client, fake, create_user, create_tags):
    r = client.post(
        '/users/test_user/notes/', json={
            'text': fake.text(max_nb_chars=200),
            'url': fake.uri(),
            'tags': [],
        },
    )
    assert r.ok
    note_id = r.json()['id']
    r = client.delete(f'/notes/{note_id}/archive')
    assert r.ok
    r = client.get(f'/notes/{note_id}')
    assert r.json()['tags'] == ['archive']

    # test when trying to archive already archived note
    r = client.delete(f'/notes/{note_id}/archive')
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json() == {'detail': {'note already archived': note_id}}

    # test unarchive note
    r = client.post(f'/notes/{note_id}/archive')
    assert r.ok
    r = client.get(f'/notes/{note_id}')
    assert 'archive' not in r.json()['tags']

    # test unarchive not-archive note error
    r = client.post(f'/notes/{note_id}/archive')
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json() == {'detail': {'note already unarchived': note_id}}


def test_get_tag_notes(client, fake, create_user, create_tags):
    client.post('/users/test_user/notes/', json={'text': fake.text(max_nb_chars=200), 'tags': ['books']})
    client.post('/users/test_user/notes/', json={'text': fake.text(max_nb_chars=200), 'tags': ['books', 'groceries']})
    client.post('/users/test_user/notes/', json={'text': fake.text(max_nb_chars=200), 'tags': ['groceries']})

    r = client.get('/tags/books/notes')
    assert r.ok
    assert [note['id'] for note in r.json()] == [1, 2]

    r = client.get('/tags/groceries/notes')
    assert r.ok
    assert [note['id'] for note in r.json()] == [2, 3]


@pytest.mark.parametrize('text', [None, 'test'])
@pytest.mark.parametrize('url', [None, 'https://test.com'])
@pytest.mark.parametrize('tags', [[], ['books']])
@pytest.mark.parametrize('edit_text', [None, 'edit_test'])
@pytest.mark.parametrize('edit_url', [None, 'https://edit.com'])
@pytest.mark.parametrize('edit_tags', [[], ['groceries'], ['books', 'groceries']])
def test_edit_note(
    client, create_user, create_tags,
    text, url, tags, edit_text, edit_url, edit_tags,
):
    r = client.post('/users/test_user/notes/', json={'text': text, 'url': url, 'tags': tags})
    assert r.ok
    initial = r.json()

    r = client.post(f'/notes/{initial["id"]}/edit/', json={'text': edit_text, 'url': edit_url, 'tags': edit_tags})
    assert r.ok
    edited = r.json()

    assert edited['text'] == edit_text
    assert edited['url'] == edit_url
    assert edited['tags'] == edit_tags
    assert initial['created_time'] == edited['created_time'], str(initial)
    assert initial['updated_time'] < edited['updated_time'], str(initial)


def test_edit_note_not_exists(client, create_user, create_tags):
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


def test_note_by_tags():
    raise
