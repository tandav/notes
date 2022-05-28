from collections.abc import Iterable
from fastapi import Header
from fastapi.responses import JSONResponse
from http import HTTPStatus
from notes_v2.config import CSS_FRAMEWORK

def drop_keys(kv: dict | Iterable[dict], keys: set[str]):
    if isinstance(kv, dict):
        return {k: v for k, v in kv.items() if k not in keys}
    return [drop_keys(kv_, keys) for kv_ in kv]


UNSUPPORTED_EXCEPTION = JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'detail': '415 Unsupported Media Type'})


class MediaType:
    # UNSUPPORTED_EXCEPTION = JSONResponse(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, content={'detail': '415 Unsupported Media Type'})

    def __init__(self, accept: Header):
        accept = accept.split(',')
        self.is_html = accept[0] == 'text/html'
        self.is_json = 'application/json' in accept or '*/*' in accept
        self.is_unsupported = not (self.is_html or self.is_json)
