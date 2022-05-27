import pytest
from notes_v2 import models



@pytest.mark.parametrize('table', [
    models.Note,
])
def test_tables_empty(db, table):
    assert db.query(table).count() == 0
