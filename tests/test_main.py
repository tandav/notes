from notes import models


def test_main(db):
    pass


def test_user(db):
    u = db.query(models.User).first()
