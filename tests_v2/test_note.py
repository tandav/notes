from http import HTTPStatus

import colortool
import pytest

from notes_v2 import util


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
        'is_private': False,
        'is_archived': False,
        'right_notes': [],
        'left_notes': [],
        'username': 'anon',
        'tag': tag,
        'tags': [],
    }
    if tag is not None:
        assert colortool.is_hex_color(j['color']) and j['color'] != '#000000', str(j)


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


def test_anon_notes_cant_be_private(client):
    r = client.post(f'/notes/', json={'is_private': True})
    assert r.status_code == HTTPStatus.UNAUTHORIZED
    assert r.json() == {'detail': 'AnonNotesCantBePrivate'}

    assert client.post(f'/notes/', json={}).json()['is_private'] == False


def test_notes_are_private_by_default_for_auth_users(client, create_users):
    auth, _ = create_users
    assert client.post('/notes/', json={}, auth=auth).json()['is_private']


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
# test delete note
# test error when try to edit/update non-existing note
# test unique constraint error when creating/updating note with tag that already exists in another note (db error should be raised)
# test notes created by anon user cant be updated/edited
# test cant create note with non existing tags/right notes
# test tags /right_notes / left_notes timestamps are updating when linked note updates
# xml etree tests
# test parse links from markdown, and backlinks are created
