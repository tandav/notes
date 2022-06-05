import datetime
import string
from collections.abc import Iterable
from functools import partial

import colortool
from fastapi import Header
from fastapi.responses import JSONResponse

from notes_v2.config import CSS_FRAMEWORK


def _ago(e) -> str:
    # e: pass timedelta between timestamps in 1579812524 format
    e *= 1000 # convert to 1579812524000 format
    t = round(e / 1000)
    n = round(t /   60)
    r = round(n /   60)
    o = round(r /   24)
    i = round(o /   30)
    a = round(i /   12)
    if   e <  0: return              'just now'
    elif t < 10: return              'just now'
    elif t < 45: return str(t) + ' seconds ago'
    elif t < 90: return          'a minute ago'
    elif n < 45: return str(n) + ' minutes ago'
    elif n < 90: return           'an hour ago'
    elif r < 24: return str(r) +   ' hours ago'
    elif r < 36: return             'a day ago'
    elif o < 30: return str(o) +    ' days ago'
    elif o < 45: return           'a month ago'
    elif i < 12: return str(i) +  ' months ago'
    elif i < 18: return            'a year ago'
    else:        return str(a) +   ' years ago'


def ago(t: datetime.datetime):
    return _ago((datetime.datetime.now() - t).total_seconds())



def drop_keys(kv: dict | Iterable[dict], keys: set[str]):
    if isinstance(kv, dict):
        return {k: v for k, v in kv.items() if k not in keys}
    return [drop_keys(kv_, keys) for kv_ in kv]


def format_time(t: datetime.datetime, absolute: bool = False) -> str:
    if absolute or (datetime.datetime.now() - t).days > 30:
        return t.strftime('%Y %b %d %H:%M')
    return ago(t)


from xml.etree import ElementTree

from notes_v2.config import CSS_FRAMEWORK

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

def is_hex_color(v: str) -> bool:
    return (v.startswith('#') and set(v[1:]) <= set(string.hexdigits))


def is_valid_xml(xml: str) -> bool:
    try:
        ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return False
    except BaseException:
        raise
    else:
        return True
