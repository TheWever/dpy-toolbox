from dpy_toolbox.core.errors import AsyncTryExceptException, TryExceptException
import string

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
    """
    Formats f-strings without raising key-errors
    """
    def __missing__(self, key):
        return ""

def tokenize(s: str, *args, **kwargs):
    """
    Replace all tokens with given kwargs

    :param str s: The str that will be tokenized
    :param args:
    :param kwargs: All tokens that will be replaced
    :return str: The tokenized string
    """
    return string.Formatter().vformat(s, args, Tokenizer(**kwargs))
