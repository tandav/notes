def test_create_note(client, create_users):
    r = client.post('/notes/', json={})
    assert r.ok, r.json()


def test_create_tag_note(client, create_users):
    assert client.post('/notes/', json={'tag': 'books'}).ok


# def test_works(db):
#     assert db.query(models.Node).all()
