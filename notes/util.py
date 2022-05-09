import datetime
import string
import colorsys


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
        return ''
    return f"<a href='{url}'>{url}</a>"


def format_time(t: datetime.datetime, absolute: bool = False) -> str:
    if absolute or (datetime.datetime.now() - t).days > 30:
        return t.strftime('%Y %b %d %H:%M')
    return ago(t)


def header(
    new_note: bool = False,
    new_tag: bool = False,
    edit_note: int = 0,
    edit_tag: int = 0,
) -> str:
    items = [
        '<a href="/notes">[notes]</a>',
        '<a href="/tags">[tags]</a>',
    ]
    if new_note:
        items.append('<a href="/new_note"><button>new note</button></a>')
    if new_tag:
        items.append('<a href="/new_tag"><button>new tag</button></a>')
    if edit_note:
        items.append(f'<a href="/notes/{edit_note}/edit"><button>edit</button></a>')
    return '\n'.join(items)


def minmax_scaler(value, oldmin, oldmax, newmin=0.0, newmax=1.0) -> float:
    '''
    >>> minmax_scaler(50, 0, 100, 0.0, 1.0)
    0.5
    >>> minmax_scaler(255, 0, 255, 0.0, 1.0)
    1.0
    '''
    return (value - oldmin) * (newmax - newmin) / (oldmax - oldmin) + newmin


RGBInt = tuple[int, int, int]
RGBFloat = tuple[float, float, float]


def to_rgb_int(color: str) -> RGBInt:
    return (
        int(color[1:3], base=16),
        int(color[3:5], base=16),
        int(color[5:7], base=16),
    )


def to_rgb_float(color: RGBInt) -> RGBFloat:
    return (
        minmax_scaler(color[0], 0, 255),
        minmax_scaler(color[1], 0, 255),
        minmax_scaler(color[2], 0, 255),
    )


def hls_to_css_hex(h, l, s) -> str:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r = int(minmax_scaler(r, 0, 1, 0, 255))
    g = int(minmax_scaler(g, 0, 1, 0, 255))
    b = int(minmax_scaler(b, 0, 1, 0, 255))
    return f'#{r:02X}{g:02X}{b:02X}'


def font_border_colors(
    color: str,
    font_threshold: float = 0.5,
    border_threshold: float = 0.9,
) -> tuple[str, str]:
    """
    determine the font color to be either black or white depending on the background color
    https://css-tricks.com/switch-font-color-for-different-backgrounds-with-css/

    :param color: hex string in #4bb9ac format
    :param font_threshold: 0..1 float. lightness value below the threshold will result in white, any above will result in black
    :param border_threshold: 0..1 float. lightness value below the threshold will result the border-color as same, any above 30% darker shade of the same color
    :return: font_color, border_color in css hex string format #4bb9ac
    """
    rgb = to_rgb_float(to_rgb_int(color))
    h, l, s = colorsys.rgb_to_hls(*rgb)
    font_color = '#ffffff' if l < font_threshold else '#000000'
    border_color = color if l < border_threshold else hls_to_css_hex(h, l * 0.7, s)
    return font_color, border_color


def tags_css(tags) -> str:
    items = []
    for tag in tags:
        font_color, border_color = font_border_colors(tag.color)
        items.append(f'''
        [id="{tag.name}"] {{
            background-color: {tag.color};
            padding: 0.25em;
            margin: 3px;
            color: {font_color};
            border: 0.1em solid {border_color};
            border-radius: 4px;
        }}
        ''')
    return '\n'.join(items)
