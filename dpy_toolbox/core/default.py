from dpy_toolbox.core.errors import AsyncTryExceptException, TryExceptException
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
