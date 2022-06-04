import pytest
from notes.util import add_notes_and_tags_links


@pytest.mark.parametrize(
    'text, expected', [
        ('', ''),
        ('fdsf', 'fdsf'),
        (' fdsf', ' fdsf'),
        ('\n fdsf', '\n fdsf'),
        ('# ', '# '),
        ('#', '#'),
        ('#-', '#-'),
        ('#_', '#_'),
        ('# 24', '# 24'),
        ('# tag', '# tag'),
        ('#24', '[#24](/notes/24)'),
        ('#tag', '[#tag](/tags/tag)'),
        ('#tag2-re', '[#tag2-re](/tags/tag2-re)'),
        ('#t_2', '[#t_2](/tags/t_2)'),
        (
            '''
        fdsf
         fdsfsd fsdf #24 fdsf sd #1
        # fdsfd
        # 1
        #
        #-
        #_23
        #tag2-re #t_2
        #tag1 #tag2
        #tag3
        ''',
            '''
        fdsf
         fdsfsd fsdf [#24](/notes/24) fdsf sd [#1](/notes/1)
        # fdsfd
        # 1
        #
        #-
        #_23
        [#tag2-re](/tags/tag2-re) [#t_2](/tags/t_2)
        [#tag1](/tags/tag1) [#tag2](/tags/tag2)
        [#tag3](/tags/tag3)
        ''',
        ),
    ],
)
def test_parse_links(text, expected):
    assert add_notes_and_tags_links(text) == expected