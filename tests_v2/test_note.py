from http import HTTPStatus

import colortool
import pytest

from notes_v2 import util
from notes_v2.crud import exceptions


@pytest.mark.parametrize('text', [None, 'test'])
@pytest.mark.parametrize('url', [None, 'https://test.com'])
@pytest.mark.parametrize('tag', [None, 'books', 'groceries'])
def test_create_note(client, create_users, text, url, tag):
    payload = {
        'text': text,
        'url': url,
        'tag': tag,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    r = client.post('/notes/', json=payload)
    assert r.ok
    j = r.json()
    assert util.drop_keys(j, {'created_time', 'updated_time', 'user_id', 'id', 'color'}) == {
        'text': text,
        'url': url,
        'is_private': True,
        'is_archived': False,
        'right_notes': [],
        'left_notes': [],
        'username': 'anon',
        'tag': tag,
        'tags': [],
    }
    if tag is not None:
        assert colortool.is_hex_color(j['color']), str(j)


@pytest.fixture
def create_3_notes(client, create_users):
    note0 = client.post('/notes/', json={}).json()
    note1 = client.post('/notes/', json={}).json()
    note2 = client.post('/notes/', json={}).json()
    return note0, note1, note2


@pytest.fixture
def create_note(client, create_users):
    auth, _, _ = create_users
    r = client.post(
        '/notes/', json={
            'text': 'test',
            'url': 'https://test.com',
            'tag': 'test_tag',
        },
        auth=auth,
    )
    return auth, r.json()


@pytest.fixture
def create_3_tags(client, create_users):
    tag0 = client.post('/notes/', json={'tag': 'books'}).json()
    tag1 = client.post('/notes/', json={'tag': 'groceries'}).json()
    tag2 = client.post('/notes/', json={'tag': 'todo'}).json()
    return tag0, tag1, tag2


def test_links(client, create_3_notes):
    note0, note1, note2 = create_3_notes
    note0_id, note1_id, note2_id = note0['id'], note1['id'], note2['id']

    note3 = client.post('/notes/', json={'right_notes': [note0_id]})
    note3_id = note3.json()['id']
    assert note3.json()['right_notes'] == [note0_id]

    # test left_notes
    note0 = client.get(f'/notes/{note0_id}')
    assert note0.json()['left_notes'] == [note3_id]

    # test many links
    note4 = client.post('/notes/', json={'right_notes': [note0_id, note3_id]})
    note4_id = note4.json()['id']
    assert note4.json()['right_notes'] == [note0_id, note3_id]

    # test left_notes
    note0 = client.get(f'/notes/{note0_id}')
    assert note0.json()['left_notes'] == [note3_id, note4_id]

    note3 = client.get(f'/notes/{note3_id}')
    assert note3.json()['left_notes'] == [note4_id]


def test_cant_link_to_non_existing_notes(client, create_3_notes):
    note0, note1, note2 = create_3_notes
    note0_id, note1_id, note2_id = note0['id'], note1['id'], note2['id']

    note3 = client.post('/notes/', json={'right_notes': [42]})
    assert note3.status_code == HTTPStatus.NOT_FOUND

    note3 = client.post('/notes/', json={'right_notes': [note0_id, 42]})
    assert note3.status_code == HTTPStatus.NOT_FOUND


def test_tag_already_exists(client, create_users):
    auth, _, _ = create_users

    # on create
    r = client.post('/notes/', json={'tag': 'books'}, auth=auth)
    assert r.ok and r.json()['tag'] == 'books'

    note_id = r.json()['id']
    assert client.post('/notes/', json={'tag': 'books'}, auth=auth).status_code == HTTPStatus.BAD_REQUEST

    # on update
    note_id2 = client.post('/notes/', json={}, auth=auth).json()['id']
    # cant use already assigned tag
    assert client.post(f'/notes/{note_id2}', json={'tag': 'books'}, auth=auth).status_code == HTTPStatus.BAD_REQUEST

    # change tag on the original note
    r = client.post(f'/notes/{note_id}', json={'tag': 'groceries'}, auth=auth)
    assert r.ok and r.json()['tag'] == 'groceries'

    # assert that now tag can be used
    assert client.post(f'/notes/{note_id2}', json={'tag': 'books'}, auth=auth).ok


def test_color_for_null_tag(client):
    assert client.post('/notes/', json={'color': '#fb7324'}).status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_tags(client, create_3_tags):
    tag0, tag1, tag2 = create_3_tags

    r = client.post('/notes/', json={})
    assert r.json()['tags'] == []
    assert r.json()['right_notes'] == []

    _tags = [tag0['tag'], tag1['tag']]
    n3 = client.post('/notes/', json={'tags': _tags}).json()
    assert n3['tags'] == _tags
    assert n3['right_notes'] == [tag0['id'], tag1['id']]
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}').json()['left_notes'] == [n3['id']]
    assert client.get(f'/notes/{tag1["id"]}').json()['left_notes'] == [n3['id']]

    # test many links
    n4 = client.post('/notes/', json={'tags': [tag0["tag"]]}).json()
    assert n4['tags'] == [tag0['tag']]
    assert n4['right_notes'] == [tag0['id']]
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}').json()['left_notes'] == [n3['id'], n4['id']]

    _tags = [tag0['tag'], 'unknown_tag']
    r = client.post('/notes/', json={'tags': _tags})
    assert r.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'kv', [
        {'text': 'test2'},
        {'url': 'https://test2.com', 'is_private': False},
        {'tag': 'books'},
        {'color': '#913241'},
        {'is_archived': True},
    ],
)
def test_update_note(client, create_note, kv):
    auth, note = create_note
    note_id = note['id']
    r = client.post(f'/notes/{note_id}', json=kv, auth=auth)
    assert r.ok
    updated = r.json()
    for k, v in kv.items():
        assert updated[k] == v
    assert note['updated_time'] < updated['updated_time']


def test_color_on_update(client, create_note):
    auth, note = create_note
    note_id = note['id']

    # update tag name without specifying color, check that color remains the same
    r = client.post(f'/notes/{note_id}', json={'tag': 'books'}, auth=auth)
    assert r.json()['color'] == note['color'], r.json()

    # update color for tag, check that it changes
    color2 = '#913241'
    r = client.post(f'/notes/{note_id}', json={'color': color2}, auth=auth)
    assert r.json()['color'] == color2

    # update both tag and color
    color3 = '#fab123'
    r = client.post(f'/notes/{note_id}', json={'tag': 'groceries', 'color': color3}, auth=auth)
    assert r.json()['color'] == color3


def test_color_is_none_if_tag_is_none(create_3_notes):
    note0, note1, note2 = create_3_notes
    assert note0['color'] is None

# test note_color is none when set update/create note w/o tag

# add theese tests for update too, (not only for create)
# assert error creating private by unauthenticated anon user
# test right_notes
# test tags
# test right_notes/left_notes and tags / links
# test backlinks / left_notes
# assert raises when creating note with none existing tags
# test edit/update note
# test archive/unarhive (updated_time should be updated)
# test public/private (updated_time should be updated)
# test anon notes are always public (error when private:true w/o auth) and user are private by default
# test delete note
# test error when try to edit/update non-existing note
# test unique constraint error when creating/updating note with tag that already exists in another note (db error should be raised)
# test notes created by anon user cant be updated/edited
# test cant create note with non existing tags/right notes
