from http import HTTPStatus


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


def test_username_already_registred(client, create_user):
    response = client.post('/users/', auth=('test_user', 'test_password'))
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'username already registered'}


def test_get_user_by_username(client, create_user):
    r = client.get('/users/test_user')
    assert r.ok
    assert r.json()['id'] == 1
