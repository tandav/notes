import pytest
from http import HTTPStatus
from notes import models
from faker import Faker
fake = Faker()


@pytest.mark.parametrize('table', [
    models.User,
    models.Note,
    models.Tag,
    models.Attachment,
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
            "is_private": False,
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
    # w/o color - check assigned
    # w/ color
    # invalid color handled
    # test create note with tags

# def create_note_with_tags():
#     pass
