import datetime
import string

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


def is_hex_color(v: str) -> bool:
    return (v.startswith('#') and set(v[1:]) <= set(string.hexdigits))


def format_url(url: str | None) -> str:
    if url is None:
        return 'null'
    return f"<a href='{url}'>{url}</a>"


def format_time(t: datetime.datetime, absolute: bool = False) -> str:
    if absolute or (datetime.datetime.now() - t).days > 30:
        return t.strftime('%Y %b %d %H:%M')
    return ago(t)


def header(
    new_note: bool = True,
) -> str:
    items = [
        '<a href="/notes">[notes]</a>',
        '<a href="/tags">[tags]</a>',

    ]
    if new_note:
        items.append('<a href="/new_note"><button>new note</button></a>',)
    return '\n'.join(items)


def tags_css(tags) -> str:
    return '\n'.join(f'''
    #{tag.name} {{
        background-color: {tag.color};
        padding: 0.25em;
        border-radius: 4px;
        margin: 3px;
    }}
    ''' for tag in tags)
