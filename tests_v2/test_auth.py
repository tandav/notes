from http import HTTPStatus

import pytest


def test_cant_edit_anon_note(client, create_users):
    auth, _ = create_users
    n_id = client.post('/notes/', json={}).json()['id']

    # test anon cant edit
    assert client.post(f'/notes/{n_id}', json={'text': 'test'}).status_code == HTTPStatus.UNAUTHORIZED

    # test authenticated user cant edit as well
    assert client.post(f'/notes/{n_id}', json={'text': 'test'}, auth=auth).status_code == HTTPStatus.UNAUTHORIZED


def test_user_can_edit_only_own_notes(client, create_users):
    auth0, auth1 = create_users
    n_id = client.post('/notes/', json={}, auth=auth0).json()['id']

    # user0 can edit note
    r = client.post(f'/notes/{n_id}', json={'text': 'test'}, auth=auth0)
    assert r.ok
    assert r.json()['text'] == 'test'

    # user1 cant edit user0's note
    assert client.post(f'/notes/{n_id}', json={'text': 'test'}, auth=auth1).status_code == HTTPStatus.UNAUTHORIZED


def test_anon_notes_are_accessible_for_auth_user(client, create_users):
    auth0, auth1 = create_users
    n_ids = [client.post('/notes/', json={}).json()['id'] for _ in range(3)]
    assert [n['id'] for n in client.get('/users/anon/notes', auth=auth0).json()] == n_ids


def test_public_auth_user_notes_are_accessible_for_anon(client, create_users):
    auth0, auth1 = create_users
    n_ids = [client.post('/notes/', json={'is_private': False}, auth=auth0).json()['id'] for _ in range(3)]
    assert [n['id'] for n in client.get(f'/users/{auth0[0]}/notes').json()] == n_ids


def test_public_auth_user_notes_are_accessible_for_other_auth_user(client): pass
def test_private_auth_user_notes_are_not_accessible_for_anon(client): pass
def test_private_auth_user_notes_are_not_accessible_for_other_auth_user(client): pass
def test_all_auth_user_notes_are_accessible_for_himself(client): pass
