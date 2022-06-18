import pytest


@pytest.mark.parametrize(
    'accept, content_type, expected', [
        ('text/html', None, 'html'),
        ('application/json', None, 'json'),
        ('text/html,application/json', None, 'html'),
        ('application/json,text/html', None, 'json'),
        ('*/*', None, 'json'),
        ('text/html', 'application/x-www-form-urlencoded', 'form'),
        ('application/json,text/html', 'application/x-www-form-urlencoded', 'form'),
        ('*/*', 'application/x-www-form-urlencoded', 'form'),
        ('*/*', 'multipart/form-data', 'form'),
    ],
)
def test_guess_type(client, accept, content_type, expected):
    headers = {}
    if accept is not None:
        headers['Accept'] = accept
    if content_type is not None:
        headers['Content-Type'] = content_type

    assert client.get('/guess_type', headers=headers).json()['recognized_media_type'] == expected
