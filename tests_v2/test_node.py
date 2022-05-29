def test_create_node(client, fake):
    response = client.post('/nodes/')
    assert response.ok, response.json()
