import pytest
from http import HTTPStatus
from notes import models


@pytest.mark.parametrize('table', [
    models.User,
    models.Note,
    models.Tag,
    models.Attachment,
])
def test_tables_empty(db, table):
    assert db.query(table).count() == 0


def test_create_item(client):
    response = client.post(
        "/users/",
        json={"username": "test_user", "password": "test_password"},
    )
    assert response.ok, response.json()
    j = response.json()
    assert j.pop('created_time')
    assert j.pop('updated_time')
    assert j == {
        'id': 1,
        'notes': [],
        'username': 'test_user',
    }


def test_username_already_registred(client):
    response = client.post(
        "/users/",
        json={"username": "test_user", "password": "test_password"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'username already registered'}
