from http import HTTPStatus

import pytest

# unify tag and right_notes tests parametrize
from notes_v2 import util


@pytest.fixture
def create_3_tags(client, create_users):
    auth, _ = create_users
    tag0 = client.post('/notes/', json={'tag': 'tag0'}, auth=auth).json()
    tag1 = client.post('/notes/', json={'tag': 'tag1'}, auth=auth).json()
    tag2 = client.post('/notes/', json={'tag': 'tag2'}, auth=auth).json()
    return auth, (tag0, tag1, tag2)


def test_empty(client, create_3_tags):
    auth, (tag0, tag1, tag2) = create_3_tags

    # on create
    r = client.post('/notes/', json={}, auth=auth)
    assert r.json()['tags'] == []
    assert r.json()['right_notes'] == []
    # on update
    r = client.post(f'/notes/{r.json()["id"]}', json={}, auth=auth)
    assert r.json()['tags'] == []
    assert r.json()['right_notes'] == []


@pytest.mark.parametrize('check_tag', [False, True])
@pytest.mark.parametrize('check_update', [False, True])
def test_create_update(client, create_3_tags, check_tag, check_update):
    auth, (tag0, tag1, tag2) = create_3_tags
    tags = [tag0['tag'], tag1['tag']]
    right_notes = [tag0['id'], tag1['id']]
    payload = {'tags': tags} if check_tag else {'right_notes': right_notes}

    if check_update:
        n3 = client.post('/notes/', json={}, auth=auth).json()
        n3 = client.post(f'/notes/{n3["id"]}', json=payload, auth=auth).json()
    else:
        n3 = client.post('/notes/', json=payload, auth=auth).json()
    assert n3['tags'] == tags
    assert n3['right_notes'] == right_notes
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n3['id']]
    assert client.get(f'/notes/{tag1["id"]}', auth=auth).json()['left_notes'] == [n3['id']]

    # test many links
    tags = [tag0['tag']]
    right_notes = [tag0['id']]
    payload = {'tags': tags} if check_tag else {'right_notes': right_notes}
    if check_update:
        n4 = client.post('/notes/', json={}, auth=auth).json()
        n4 = client.post(f'/notes/{n4["id"]}', json=payload, auth=auth).json()
    else:
        n4 = client.post('/notes/', json=payload, auth=auth).json()
    assert n4['tags'] == tags
    assert n4['right_notes'] == right_notes
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n3['id'], n4['id']]

    # test update back to empty
    if not check_update:
        return
    tags = []
    right_notes = []
    payload = {'tags': tags} if check_tag else {'right_notes': right_notes}
    n3 = client.post(f'/notes/{n3["id"]}', json=payload, auth=auth).json()
    assert n3['tags'] == tags
    assert n3['right_notes'] == right_notes

    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n4['id']]
    assert client.get(f'/notes/{tag1["id"]}', auth=auth).json()['left_notes'] == []


def test_tag_not_found(client, create_3_tags):
    # todo: on update
    auth, (tag0, tag1, tag2) = create_3_tags
    _tags = [tag0['tag'], 'unknown_tag']
    r = client.post('/notes/', json={'tags': _tags}, auth=auth)
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_tag_already_exists(client, create_users):
    # todo: on update
    auth, _ = create_users

    # on create
    r = client.post('/notes/', json={'tag': 'tag0'}, auth=auth)
    assert r.ok and r.json()['tag'] == 'tag0'

    note_id = r.json()['id']
    assert client.post('/notes/', json={'tag': 'tag0'}, auth=auth).status_code == HTTPStatus.BAD_REQUEST

    # on update
    note_id2 = client.post('/notes/', json={}, auth=auth).json()['id']
    # cant use already assigned tag
    assert client.post(f'/notes/{note_id2}', json={'tag': 'tag0'}, auth=auth).status_code == HTTPStatus.BAD_REQUEST

    # change tag on the original note
    r = client.post(f'/notes/{note_id}', json={'tag': 'tag1'}, auth=auth)
    assert r.ok and r.json()['tag'] == 'tag1'

    # assert that now tag can be used
    assert client.post(f'/notes/{note_id2}', json={'tag': 'tag0'}, auth=auth).ok


def test_cant_update_left_notes(client, create_note):
    auth, note = create_note
    assert client.post(f'/notes/{note["id"]}', json={'left_notes': [4, 2]}, auth=auth).json()['left_notes'] == []


def test_test_updated_time_on_create(client, create_3_tags):
    """Note.updated_time should updates when reference to Note is updated"""
    auth, (tag0, tag1, tag2) = create_3_tags

    # add reference to tag0, tag1
    client.post('/notes/', json={'tags': [tag0['tag']]}, auth=auth).json()
    tag0_t0 = client.get(f'/notes/{tag0["id"]}', auth=auth).json()['updated_time']
    assert tag0['updated_time'] < tag0_t0


def test_test_updated_time_on_update(client, create_3_tags):
    """Note.updated_time should updates when reference to Note is updated"""
    auth, (tag0, tag1, tag2) = create_3_tags

    note_id = client.post('/notes/', json={}, auth=auth).json()['id']

    # add reference to tag0, tag1
    client.post(f'/notes/{note_id}', json={'tags': [tag0['tag'], tag1['tag']]}, auth=auth).json()
    tag0_t0 = client.get(f'/notes/{tag0["id"]}', auth=auth).json()['updated_time']
    tag1_t0 = client.get(f'/notes/{tag1["id"]}', auth=auth).json()['updated_time']
    assert tag0['updated_time'] < tag0_t0
    assert tag1['updated_time'] < tag1_t0

    # update reference to tag0, tag2
    client.post(f'/notes/{note_id}', json={'tags': [tag1['tag'], tag2['tag']]}, auth=auth).json()
    tag1_t1 = client.get(f'/notes/{tag1["id"]}', auth=auth).json()['updated_time']
    tag2_t1 = client.get(f'/notes/{tag2["id"]}', auth=auth).json()['updated_time']
    assert tag1_t0 == tag1_t1  # should be unchanged
    assert tag2['updated_time'] < tag2_t1
