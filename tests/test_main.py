import pytest
from notes import models
from notes import crud
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from notes import models
from notes.server import get_db
from notes.server import app
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
# app.dependency_overrides[get_db] = db


# @pytest.mark.parametrize('table', [
#     models.User,
#     models.Note,
#     models.Tag,
#     models.Attachment,
# ])
# def test_tables_empty(db, table):
#     assert db.query(table).count() == 0


# engine = create_engine('sqlite:///./test.db', connect_args={"check_same_thread": False})
# engine = create_engine('sqlite:///:memory:', connect_args={"check_same_thread": False}, echo=True)
engine = create_engine('sqlite://', connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# def test_create_item(client):
def test_create_item():
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


# @pytest.mark.xfail
# def test_username_already_registred():
#     raise NotImplementedError
