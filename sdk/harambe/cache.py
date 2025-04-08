from functools import wraps
from typing import Any


def single_value_cache(cache_attr: str):
    """
    Decorator factory to cache a single (key, value) tuple on `self`.
    :param cache_attr: name of the attribute on self that holds the cache tuple.
    """

    def decorator(fn):
        @wraps(fn)
        async def wrapper(self, key: Any, *args, **kwargs):
            cache = getattr(self, cache_attr, None)
            if cache is not None and cache[0] == key:
                return cache[1]

            result = await fn(self, key, *args, **kwargs)
            setattr(self, cache_attr, (key, result))

            return result

        return wrapper

    return decorator
