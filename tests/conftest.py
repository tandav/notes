import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from notes import models
from notes.server import get_db
from notes.server import app
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool


# @pytest.fixture(scope='session')
# def engine():
#     return create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, echo=True)
#

@pytest.fixture(scope='session', autouse=True)
def db():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool, echo=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # models.Base.metadata.drop_all(bind=engine)
        db.close()


# @pytest.fixture(scope='session', autouse=True)
# def client():
#     engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, echo=True)
#     TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     models.Base.metadata.create_all(bind=engine)
#     def override_get_db():
#         try:
#             db = TestingSessionLocal()
#             yield db
#         finally:
#             # models.Base.metadata.drop_all(bind=engine)
#             db.close()
#     app.dependency_overrides[get_db] = override_get_db
#     # app.dependency_overrides[get_db] = db
#     yield TestClient(app)


# engine = create_engine('sqlite:///:memory:', connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# models.Base.metadata.create_all(bind=engine)



@pytest.fixture(scope='session', autouse=True)
def client(db):
    def override_get_db():
        yield db
        # try:
        #     db = TestingSessionLocal()
        #     yield db
        # finally:
        #     db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

