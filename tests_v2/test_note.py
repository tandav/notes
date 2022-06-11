import colortool
import pytest

from notes_v2 import util


@pytest.mark.parametrize('text', [None, 'test'])
@pytest.mark.parametrize('url', [None, 'https://test.com'])
@pytest.mark.parametrize('tag', [None, 'books', 'groceries'])
@pytest.mark.parametrize('json_payload', [None, {"k0": [1,2], "k1": None, "k3": {"k3.0": 1}}])
def test_create_note(client, create_users, text, url, tag, json_payload):
    payload = {'text': text, 'url': url, 'tag': tag, 'json_payload': json_payload}
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
        'username': 'anon',
        'tag': tag,
        'tags': [],
        'json_payload': json_payload,
    }
    assert colortool.is_hex_color(j['color'])


def test_right_notes(client, create_users):
    n0_id = client.post('/notes/', json={}).json()['id']
    n1_id = client.post('/notes/', json={}).json()
    n2_id = client.post('/notes/', json={}).json()
    n3 = client.post('/notes/', json={'right_notes': [n0_id]})

    assert n3.ok


@pytest.mark.parametrize('tags', [['books'], ['books', 'groceries']])
def test_create_note_with_tags(client, create_tags, tags):
    r = client.post('/notes/', json={'tags': tags})
    assert r.json()['tags'] == tags


def test_tags(client, create_tags):
    assert True
    # assert [note['tag'] for note in client.get('/tags/').json()] == ['books', 'groceries']


    # r =
    # assert r.json() == []

#     # test_create_tag_note
#     r = client.post('/notes/', json={'tag': 'books'})
#     assert r.ok
#     assert r.json()['tag'] == 'books'
#
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


# assert error creating private by unauthenticated anon user
# test right_notes
# test tags
# test right_notes and tags
# test backlinks / left_notes
# assert raises when creating note with none existing tags
# test json payload
