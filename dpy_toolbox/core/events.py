from typing import Optional, Callable, Iterable
from .errors import NoEventFunction

DEFAULT_EVENT_TAG_RESOLVER = {
            "pass_bot": (lambda var: getattr(var["self"], "bot")),
            "pass_self": (lambda var: var["self"]),
            "pass_event": (lambda var: var["event_type"])
        }

DEFAULT_EVENT_TAGS = set(DEFAULT_EVENT_TAG_RESOLVER)

class EventFunction:
    def __init__(
            self,
            func: Optional[Callable] = None,
            events: Optional[Iterable[str]] = None,
            tags: Optional[Iterable[str]] = None,
            tag_resolver: Optional[dict[str]] = None
    ):
        self.wait_for_events = events if events else []
        self.func = func
        self.tags = tags or ()
        self.tag_resolver = tag_resolver or DEFAULT_EVENT_TAG_RESOLVER

    async def __call__(self, *args, **kwargs):
        if not self.func:
            raise NoEventFunction(f"{self.func} is of type {type(self.func)}")
        return await self.func(*args, **kwargs)

class EventFunctionWrapper:
    def __init__(self, events: Optional[list[str]] = None, tag_resolver: Optional[dict[Callable]] = None, **kwargs):
        self.wait_for_events = events if events else []

        self.tags = list(filter(lambda x: x[1], kwargs))
        self.tag_resolver = tag_resolver or DEFAULT_EVENT_TAG_RESOLVER.copy()
        if any(x not in self.tag_resolver for x in self.tags):
            raise TypeError()

    def __call__(self, f):
        return EventFunction(f, self.wait_for_events, self.tags, self.tag_resolver)
