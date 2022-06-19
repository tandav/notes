from http import HTTPStatus

import colortool


def test_color_for_when_tag_is_null(client, create_user):
    auth = create_user
    assert client.post('/notes/', json={'color': '#fb7324'}).status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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

    # 'test when updating note wiht tag=None, color=None and providing only tag, assert that random color is assigned
    n = client.post('/notes/', json={}, auth=auth).json()  # create empty note
    assert n['tag'] is None
    assert n['color'] is None
    note_id = n['id']
    color = client.post(f'/notes/{note_id}', json={'tag': 'books'}, auth=auth).json()['color']
    assert colortool.is_hex_color(color) and color != '#000000'


def test_color_is_none_if_tag_is_none(client, create_users):
    auth, _ = create_users

    # on create
    note = client.post('/notes/', json={}, auth=auth).json()
    assert note['color'] is None

    # on update
    assert client.post(f'/notes/{note["id"]}', json={'text': 'test123'}, auth=auth).json()['color'] is None
