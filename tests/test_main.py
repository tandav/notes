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

# app.dependency_overrides[get_db] = db


# @pytest.mark.parametrize('table', [
#     models.User,
#     models.Note,
#     models.Tag,
#     models.Attachment,
# ])
# def test_tables_empty(db, table):
#     assert db.query(table).count() == 0





SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }


# @pytest.mark.xfail
# def test_username_already_registred():
#     raise NotImplementedError
