from fastapi.templating import Jinja2Templates

from notes_v2 import util

templates = Jinja2Templates(directory='notes_v2/templates')
templates.env.filters['format_time'] = util.format_time
