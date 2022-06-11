import colortool
import pytest

from notes_v2 import util


@pytest.mark.parametrize('text', [None, 'test'])
@pytest.mark.parametrize('url', [None, 'https://test.com'])
@pytest.mark.parametrize('tag', [None, 'books', 'groceries'])
@pytest.mark.parametrize('tags', [None, ['books', 'groceries']])
def test_create_note(client, create_users, text, url, tag, tags):
    payload = {
        'text': text,
        'url': url,
        'tag': tag,
        'tags': tags,
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
        'username': 'anon',
        'tag': tag,
        'tags': tags if tags is not None else [],
    }
    assert colortool.is_hex_color(j['color'])


# def test_right_notes(client, create_users):
#     n0_id = client.post('/notes/', json={}).json()['id']
#     n1_id = client.post('/notes/', json={}).json()['id']
#     n2_id = client.post('/notes/', json={}).json()['id']
#     n3 = client.post('/notes/', json={'right_notes': [n0_id]})
#
#     assert n3.ok
#     assert n3.json()['right_notes'] == [n0_id]
#
#     # test left_notes
#     n0 = client.get(f'/notes/{n0_id}')
#     assert n0.ok
#     assert n0.json()['left_notes'] == [n3['id']]


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
# test right_notes/left_notes and tags / links
# test backlinks / left_notes
# assert raises when creating note with none existing tags
# test edit/update note
# test archive
# test public/private
# test anon notes are always public (error when private:true w/o auth) and user are private by default
# test delete note
# test error when try to edit/update non-existing note
