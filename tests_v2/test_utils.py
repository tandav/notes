import pytest

from notes_v2.dependencies import guess_type


@pytest.mark.parametrize(
    'accept, expected', [
        ('text/html', 'html'),
        ('application/json', 'json'),
        ('text/html,application/json', 'html'),
        ('application/json,text/html', 'json'),
        ('*/*', 'json'),
    ],
)
def test_guess_type(accept, expected):
    assert guess_type(accept) == expected
