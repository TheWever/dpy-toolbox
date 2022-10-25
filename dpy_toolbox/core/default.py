from dpy_toolbox.core.errors import AsyncTryExceptException, TryExceptException

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