import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from notes import models
from notes.server import app, get_db
from faker import Faker


# @pytest.fixture(scope='session')
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
    try:
        yield db
    finally:
        # models.Base.metadata.drop_all(bind=engine)
        db.close()


# @pytest.fixture(scope='session')
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
    yield client.post('/users/', auth=('test_user', 'test_password'))


@pytest.fixture
def create_tags(client):
    client.post('/tags/', json={'name': 'books', 'color': '#c0ffee'})
    client.post('/tags/', json={'name': 'archive', 'color': '#f0ffff'})
    client.post('/tags/', json={'name': 'groceries'})
