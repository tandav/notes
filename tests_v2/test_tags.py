from http import HTTPStatus

import pytest


@pytest.fixture
def create_3_tags(client, create_users):
    auth, _, _ = create_users
    tag0 = client.post('/notes/', json={'tag': 'books'}, auth=auth).json()
    tag1 = client.post('/notes/', json={'tag': 'groceries'}, auth=auth).json()
    tag2 = client.post('/notes/', json={'tag': 'todo'}, auth=auth).json()
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


def test_create(client, create_3_tags):
    auth, (tag0, tag1, tag2) = create_3_tags
    _tags = [tag0['tag'], tag1['tag']]
    n3 = client.post('/notes/', json={'tags': _tags}, auth=auth).json()
    assert n3['tags'] == _tags
    assert n3['right_notes'] == [tag0['id'], tag1['id']]
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n3['id']]
    assert client.get(f'/notes/{tag1["id"]}', auth=auth).json()['left_notes'] == [n3['id']]


def test_update(client, create_3_tags):
    auth, (tag0, tag1, tag2) = create_3_tags
    _tags = [tag0['tag'], tag1['tag']]
    n3 = client.post('/notes/', json={}, auth=auth).json()
    n3 = client.post(f'/notes/{n3["id"]}', json={'tags': _tags}, auth=auth).json()
    assert n3['tags'] == _tags
    assert n3['right_notes'] == [tag0['id'], tag1['id']]
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n3['id']]
    assert client.get(f'/notes/{tag1["id"]}', auth=auth).json()['left_notes'] == [n3['id']]



def test_update_empty():
    pass

    # test set back to empty





def test_tags(client, create_3_tags):
    auth, (tag0, tag1, tag2) = create_3_tags

    # test tags and right notes returned when tags are provided
    # on create
    _tags = [tag0['tag'], tag1['tag']]
    n3 = client.post('/notes/', json={'tags': _tags}, auth=auth).json()
    assert n3['tags'] == _tags
    assert n3['right_notes'] == [tag0['id'], tag1['id']]
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n3['id']]
    assert client.get(f'/notes/{tag1["id"]}', auth=auth).json()['left_notes'] == [n3['id']]
    # on update

    # test many links
    n4 = client.post('/notes/', json={'tags': [tag0["tag"]]}, auth=auth).json()
    assert n4['tags'] == [tag0['tag']]
    assert n4['right_notes'] == [tag0['id']]
    # test left_notes updated as well
    assert client.get(f'/notes/{tag0["id"]}', auth=auth).json()['left_notes'] == [n3['id'], n4['id']]

    _tags = [tag0['tag'], 'unknown_tag']
    r = client.post('/notes/', json={'tags': _tags}, auth=auth)
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_tag_already_exists(client, create_users):
    # todo: on update
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


@pytest.mark.xfail
def test_cant_update_left_notes():
    raise NotImplementedError('TODO')
