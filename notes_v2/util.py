from collections.abc import Iterable


def drop_keys(kv: dict | Iterable[dict], keys: set[str]):
    if isinstance(kv, dict):
        return {k: v for k, v in kv.items() if k not in keys}
    return [drop_keys(kv_, keys) for kv_ in kv]

