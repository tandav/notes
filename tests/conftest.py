import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope='session')
def engine():
    return create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, echo=True)


@pytest.fixture(scope='session')
def db(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
