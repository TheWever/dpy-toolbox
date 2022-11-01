from dpy_toolbox.core.errors import AsyncTryExceptException, TryExceptException
from typing import Callable, Coroutine, Any, Union
from functools import wraps
import asyncio
import string


class MISSING:
    def get(self, val=None, alt=None, *args, **kwargs):
        return alt

    def __get__(self, instance, owner):
        raise

    def __getattribute__(self, item):
        raise

    def __bool__(self):
        return None


async def async_try_exc(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except Exception as exc:
        return AsyncTryExceptException(exc)


def try_exc(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        return TryExceptException(exc)


class Tokenizer(dict):
    def __missing__(self, key):
        return ""


def tokenize(s: str, *args, **kwargs):
    return string.Formatter().vformat(s, args, Tokenizer(**kwargs))


def ensure_coroutine(
        func: Callable
) -> Union[Callable[[tuple[Any, ...], dict[str, Any]], Coroutine[Any, Any, Any]], Callable[..., Any]]:
    """Returns awaitable func"""
    @wraps(func)
    async def awaitable(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return awaitable if not asyncio.iscoroutinefunction(func) else func

async def await_any(func, *args, **kwargs):
    return await ensure_coroutine(func)(*args, **kwargs)

def set_multikey_dict_item(obj: dict, val, *args):
    if len(args) <= 1:
        obj.__setitem__(args[0], val)
        return obj
    if args[0] not in obj:
        obj[args[0]] = {}
    return set_multikey_dict_item(obj[args[0]], val, *args[1:])

def get_multikey_dict_item(obj: dict, *args):
    if len(args) <= 1:
        return obj.__getitem__(args[0])
    return get_multikey_dict_item(obj[args[0]], *args[1:])
