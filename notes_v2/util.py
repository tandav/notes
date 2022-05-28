from collections.abc import Iterable
from fastapi import Header
from fastapi.responses import JSONResponse
from http import HTTPStatus
from notes_v2.config import CSS_FRAMEWORK

def drop_keys(kv: dict | Iterable[dict], keys: set[str]):
    if isinstance(kv, dict):
        return {k: v for k, v in kv.items() if k not in keys}
    return [drop_keys(kv_, keys) for kv_ in kv]
