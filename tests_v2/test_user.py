from http import HTTPStatus

from notes_v2 import util


def test_create_user(client, fake):
    response = client.post('/users/', auth=('test_user', 'test_password'))
    assert response.ok, response.json()
    j = response.json()
    assert j.pop('created_time')
    assert j.pop('updated_time')
    assert j == {
        'id': 1,
        'username': 'test_user',
    }

    # create more users
    for _ in range(2):
        username = fake.user_name()
        password = fake.password(length=32, special_chars=False)
        assert client.post('/users/', auth=(username, password)).ok


def test_already_registred(client, create_user):
    response = client.post('/users/', auth=('test_user', 'test_password'))
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'username already registered'}


def test_get_user_by_username(client, create_user):
    r = client.get('/users/test_user')
    assert r.ok
    assert r.json()['id'] == 1


def test_read(client, create_users):
    drop_keys = {'created_time', 'updated_time'}
    assert util.drop_keys(client.get('/users/').json(), drop_keys) == [
        {'id': 1, 'username': 'test_user1'},
        {'id': 2, 'username': 'test_user2'},
        {'id': 3, 'username': 'anon'},
    ]

    # test pagination
    assert util.drop_keys(client.get('/users/?skip=1&limit=1').json(), drop_keys) == [
        {'id': 2, 'username': 'test_user2'},
    ]
