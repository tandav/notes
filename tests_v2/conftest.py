import pytest
from faker import Faker
from fastapi.security import HTTPBasicCredentials
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import notes_v2.crud.user
from notes_v2 import models
from notes_v2.dependencies import get_db
from notes_v2.server import app


@pytest.fixture(scope='class')
def db():
    engine = create_engine(
        'sqlite:///:memory:',
        # 'sqlite:///./test.db',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        # echo=True,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    notes_v2.crud.user.create(db, HTTPBasicCredentials(username='anon', password=''))
    yield db
    # models.Base.metadata.drop_all(bind=engine)
    db.close()


@pytest.fixture(scope='class')
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # with TestClient(app) as q: # https://fastapi.tiangolo.com/advanced/testing-events/ (not works)
    #     yield q


@pytest.fixture(scope='class')
def fake():
    yield Faker()


@pytest.fixture(scope='class')
def create_user(client):
    auth = 'test_user', 'test_password'
    client.post('/users/', auth=auth)
    return auth

@pytest.fixture(scope='class')
def create_users(client):
    auth0 = 'test_user0', 'test_password0'
    auth1 = 'test_user1', 'test_password1'
    client.post('/users/', auth=auth0)
    client.post('/users/', auth=auth1)
    return auth0, auth1


@pytest.fixture(scope='class')
def create_tags(client, create_users):
    client.post('/notes/', json={'tag': 'books'})
    client.post('/notes/', json={'tag': 'groceries'})


@pytest.fixture
def create_3_notes(client, create_users):
    note0 = client.post('/notes/', json={}).json()
    note1 = client.post('/notes/', json={}).json()
    note2 = client.post('/notes/', json={}).json()
    return note0, note1, note2


@pytest.fixture
def create_note(client, create_user):
    auth = create_user
    r = client.post(
        '/notes/', json={
            'text': 'test',
            'url': 'https://test.com',
            'tag': 'test_tag',
        },
        auth=auth,
    )
    return auth, r.json()
