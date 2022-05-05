from notes import models


def test_create_all(db, engine):
    models.Base.metadata.create_all(bind=engine)


def test_user(db):
    u = db.query(models.User).first()
