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
