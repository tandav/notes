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
    assert colortool.is_hex_color(j['color'])


@pytest.fixture
def create_3_notes(client, create_users):
    n0_id = client.post('/notes/', json={}).json()['id']
    n1_id = client.post('/notes/', json={}).json()['id']
    n2_id = client.post('/notes/', json={}).json()['id']
    return n0_id, n1_id, n2_id


@pytest.fixture
def create_3_tags(client, create_users):
    tag0 = client.post('/notes/', json={'tag': 'books'}).json()
    tag1 = client.post('/notes/', json={'tag': 'groceries'}).json()
    tag2 = client.post('/notes/', json={'tag': 'todo'}).json()
    return tag0, tag1, tag2


def test_links(client, create_3_notes):
    n0_id, n1_id, n2_id = create_3_notes

    n3 = client.post('/notes/', json={'right_notes': [n0_id]})
    n3_id = n3.json()['id']
    assert n3.json()['right_notes'] == [n0_id]

    # test left_notes
    n0 = client.get(f'/notes/{n0_id}')
    assert n0.json()['left_notes'] == [n3_id]

    # test many links
    n4 = client.post('/notes/', json={'right_notes': [n0_id, n3_id]})
    n4_id = n4.json()['id']
    assert n4.json()['right_notes'] == [n0_id, n3_id]

    # test left_notes
    n0 = client.get(f'/notes/{n0_id}')
    assert n0.json()['left_notes'] == [n3_id, n4_id]

    n3 = client.get(f'/notes/{n3_id}')
    assert n3.json()['left_notes'] == [n4_id]


def test_cant_link_to_non_existing_notes(client, create_3_notes):
    n0_id, n1_id, n2_id = create_3_notes

    n3 = client.post('/notes/', json={'right_notes': [42]})
    assert n3.status_code == HTTPStatus.NOT_FOUND

    n3 = client.post('/notes/', json={'right_notes': [n0_id, 42]})
    assert n3.status_code == HTTPStatus.NOT_FOUND


def test_tag_already_exists(client, create_users):
    assert client.post('/notes/', json={'tag': 'books'}).ok
    r = client.post('/notes/', json={'tag': 'books'})
    assert r.status_code == HTTPStatus.BAD_REQUEST


def test_tags(client, create_3_tags):
    tag0, tag1, tag2 = create_3_tags

    r = client.post('/notes/', json={})
    assert r.json()['tags'] == []
    assert r.json()['right_notes'] == []

    _tags = [tag0['tag'], tag1['tag']]
    r = client.post('/notes/', json={'tags': _tags})
    assert r.ok, _tags
    assert r.json()['tags'] == _tags
    assert r.json()['right_notes'] == [tag0['id'], tag1['id']]

    _tags = [tag0['tag'], 'unknown_tag']
    r = client.post('/notes/', json={'tags': _tags})
    assert r.status_code == HTTPStatus.NOT_FOUND


# def test_tags_links(client, create_3_tags):
#     n0_tag, n1_tag, n2_tag = create_3_tags
#
#     n3 = client.post('/notes/', json={'tags': [n0_id]})
    # n3_id = n3.json()['id']
    # assert n3.json()['right_notes'] == [n0_id]
    #
    # # test left_notes
    # n0 = client.get(f'/notes/{n0_id}')
    # assert n0.json()['left_notes'] == [n3_id]
    #
    # # test many links
    # n4 = client.post('/notes/', json={'right_notes': [n0_id, n3_id]})
    # n4_id = n4.json()['id']
    # assert n4.json()['right_notes'] == [n0_id, n3_id]
    #
    # # test left_notes
    # n0 = client.get(f'/notes/{n0_id}')
    # assert n0.json()['left_notes'] == [n3_id, n4_id]
    #
    # n3 = client.get(f'/notes/{n3_id}')
    # assert n3.json()['left_notes'] == [n4_id]


# @pytest.mark.parametrize('tags', [['books'], ['books', 'groceries']])
# def test_create_note_with_tags(client, create_tags, tags):
#     r = client.post('/notes/', json={'tags': tags})
#     assert r.json()['tags'] == tags


# def test_tags(client, create_tags):
#     assert True
#     # assert [note['tag'] for note in client.get('/tags/').json()] == ['books', 'groceries']
#

    # r =
    # assert r.json() == []


#     # create note with tags
#     r = client.post('/notes/', json={'tags': ['books']})
#     breakpoint()
#
#     R = r.json()
#     assert r.ok
#     assert r.json()['tags'] == ['books'], r.json()
#
#
# # def test_note_user():
# #     test anon
#

# add theese tests for update too, (not only for create)

# assert error creating private by unauthenticated anon user
# test right_notes
# test tags
# test right_notes/left_notes and tags / links
# test backlinks / left_notes
# assert raises when creating note with none existing tags
# test edit/update note
# test archive
# test public/private
# test anon notes are always public (error when private:true w/o auth) and user are private by default
# test delete note
# test error when try to edit/update non-existing note
# test unique constraint error when creating/updating note with tag that already exists in another note (db error should be raised)
# test notes created by anon user cant be updated/edited
# test cant create note with non existing tags/right notes
