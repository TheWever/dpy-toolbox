import sys


class ToolboxException(Exception):
    """The base exception class all dpy-toolbox exceptions inherit from"""
    def __init__(self, *args):
        self.exc = args

    def __call__(self, *args, **kwargs):
        sys.stderr.write(" ".join(args))

class NoEventFunction(ToolboxException):
    """
    There is no function attached to the event
    """
    pass

class NotAllowed(ToolboxException):
    """
    A user was prevented from performing an action he was not allowed to perform
    """
    pass

class AsyncTryExceptException(ToolboxException):
    """
    The asynchronous try/except function has resulted in an error
    """
    pass

class TryExceptException(ToolboxException):
    """
    The non-asynchronous try/except function has resulted in an error
    """
    pass