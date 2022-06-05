import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from notes_v2 import models
from notes_v2.dependencies import get_db
from notes_v2.server import app


@pytest.fixture
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
    yield db
    # models.Base.metadata.drop_all(bind=engine)
    db.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def fake():
    yield Faker()


@pytest.fixture
def create_user(client):
    client.post('/users/', auth=('test_user', 'test_password'))


@pytest.fixture
def create_users(client):
    client.post('/users/', auth=('test_user1', 'test_password1'))
    client.post('/users/', auth=('test_user2', 'test_password2'))
    client.post('/users/', auth=('anon', 'test_password3'))


@pytest.fixture
def create_tags(client, create_users):
    client.post('/notes/', json={'tag': 'books'})
    client.post('/notes/', json={'tag': 'groceries'})


# @pytest.fixture
# def create_tags(client):
#     client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
#     client.post('/tags/', json={'name': 'archive', 'color': '#f0ffff'})
#     client.post('/tags/', json={'name': 'groceries'})
