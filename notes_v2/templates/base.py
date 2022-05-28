from textwrap import dedent
from notes_v2.config import CSS_FRAMEWORK
from xml.etree import ElementTree


# def header(
#     new_note: bool = False,
#     new_tag: bool = False,
#     edit_note: int = 0,
#     edit_tag: int = 0,
#     signup: bool = False,
#     signin: bool = False,
#     signout: bool = False,
#     username: str | None = None,
#     tag_notes_archive: str | None = False,
#     notes_archive: bool = False,
#     delete_tag: bool = False,
# ) -> str:
#     items = [
#         '<a href="/notes/">[notes]</a>',
#         '<a href="/tags/">[tags]</a>',
#     ]
#     if tag_notes_archive:
#         items.append(f'<a href="/tags/{tag_notes_archive}/archive">[archive]</a>',)
#     if notes_archive:
#         items.append(f'<a href="/tags/archive">[archive]</a>',)
#     if new_note:
#         items.append('<a href="/new_note"><button>new note</button></a>')
#     if new_tag:
#         items.append('<a href="/new_tag"><button>new tag</button></a>')
#     if edit_note:
#         items.append(f'<a href="/notes/{edit_note}/edit"><button>edit</button></a>')
#     if signup:
#         items.append('<a href="/signup">[signup]</a>')
#     if signin:
#         items.append('<a href="/signin">[signin]</a>')
#     if signout:
#         items.append('<a href="/signout">[signout]</a>')
#     if username:
#         items.append(f'<a href="/users/{username}">[{username}]</a>')
#     if delete_tag:
#         items.append('''<button class="delete_button" onclick='delete_tag("{name}")'>delete tag</button>''')
#     return CSS_FRAMEWORK + '\n' + '\n'.join(items)
#
#
# class HtmlTemplate:
#     def __init__(
#         self,
#         new_note: bool = False,
#         new_tag: bool = False,
#         edit_note: int = 0,
#         edit_tag: int = 0,
#         signup: bool = False,
#         signin: bool = False,
#         signout: bool = False,
#         username: str | None = None,
#         tag_notes_archive: str | None = False,
#         notes_archive: bool = False,
#         delete_tag: bool = False,
#         css: str | None = None,
#     ):
#         self.new_note = new_note
#         self.new_tag = new_tag
#         self.edit_note = edit_note
#         self.edit_tag = edit_tag
#         self.signup = signup
#         self.signin = signin
#         self.signout = signout
#         self.username = username
#         self.tag_notes_archive = tag_notes_archive
#         self.notes_archive = notes_archive
#         self.delete_tag = delete_tag
#
#         self.css = css or ''
#
#     def str(self):
#         return dedent(f'''
#         <html>
#         <head>
#         {CSS_FRAMEWORK}
#         </head>
#         <body>
#         <nav>
#         {header}
#         </nav>
#         <h1>Notes</h1>
#         {table_html}
#         ''' + f'''
#         <style>
#         {self.css}
#         </style>
#         </body>
#         </html>
#         ''')


def is_valid_xml(xml: str) -> bool:
    try:
        ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return False
    except:
        raise
    else:
        return True
