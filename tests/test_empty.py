import pytest
from notes import models


@pytest.mark.parametrize(
    'table', [
        models.User,
        models.Note,
        models.Tag,
        # models.Attachment,
    ],
)
def test_tables_empty(db, table):
    assert db.query(table).count() == 0
