import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from notes import models
from notes.server import app, get_db


@pytest.fixture(scope='session')
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


@pytest.fixture(scope='session')
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

