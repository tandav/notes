import pytest
from http import HTTPStatus
from notes import models
from faker import Faker
from notes.util import is_hex_color
fake = Faker()


@pytest.mark.parametrize('table', [
    models.User,
    models.Note,
    models.Tag,
    # models.Attachment,
])
def test_tables_empty(db, table):
    assert db.query(table).count() == 0


def test_create_user(client):
    response = client.post("/users/", json={"username": "test_user", "password": "test_password"})
    assert response.ok, response.json()
    j = response.json()
    assert j.pop('created_time')
    assert j.pop('updated_time')
    assert j == {
        'id': 1,
        'notes': [],
        'username': 'test_user',
    }

    # create more users
    for _ in range(2):
        username = fake.user_name()
        password = fake.password(length=32, special_chars=False)
        assert client.post("/users/", json={"username": username, "password": password}).ok


def test_username_already_registred(client):
    response = client.post(
        "/users/",
        json={"username": "test_user", "password": "test_password"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'username already registered'}


def test_create_note(client):
    for _ in range(100):
        r = client.post('/users/test_user/notes/', json={
            "title": fake.text(max_nb_chars=30),
            "text": fake.text(max_nb_chars=200),
            # "is_private": False,
            "tags": [],
        })
        assert r.ok, r.json()


# def test_read_notes(client):
#     r = client.get('')
#     breakpoint()

def test_create_tags(client):
    r = client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
    assert r.ok

    # test already created
    r = client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json() == {'detail': 'tag with name books username already exists'}

    # test valid color generated
    r = client.post('/tags/', json={'name': 'groceries'})
    assert is_hex_color(r.json()['color'])

    r = client.post('/tags/', json={'name': 'fake', 'color': 'bad-color'})
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_note_with_tags(client):
    # 1 tag
    r = client.post('/users/test_user/notes/', json={
        "title": fake.text(max_nb_chars=30),
        "text": fake.text(max_nb_chars=200),
        "tags": ['books'],
    })
    assert r.ok

    # 2 tag
    r = client.post('/users/test_user/notes/', json={
        "title": fake.text(max_nb_chars=30),
        "text": fake.text(max_nb_chars=200),
        "tags": ['books', 'groceries'],
    })
    assert r.ok

    # test error when tags does not exists
    r = client.post('/users/test_user/notes/', json={
        "title": fake.text(max_nb_chars=30),
        "text": fake.text(max_nb_chars=200),
        "tags": ['books', 'groceries', 'tag_does_not_exist'],
    })
    assert r.status_code == HTTPStatus.BAD_REQUEST

