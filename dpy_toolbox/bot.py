from typing import Union, Callable
from discord.ext import commands
import discord
from .sink import to_SinkVoiceClient, MP3Sink, SinkVoiceClient, SinkVoiceChannel, to_SinkVoiceChannel

from .core import (
    EventFunctionWrapper
)

from .ui import *
from .CustomContext import CustomContext
from .EmojiReact import EmojiReact as _EmojiReact
from .EmojiReact import EmojiReactRoler as _EmojiReactRoler

__all__ = (
    "toolbox",
    "Bot",
    "ButtonReact",
    "ButtonReactRoler",
    "ButtonDisplay",
    "to_SinkVoiceClient",
    "SinkVoiceClient",
    "MP3Sink",
    "SinkVoiceChannel",
    "to_SinkVoiceChannel"
)



class toolbox:
    DEFAULT_EVENTS = (
        "on_message",
        "on_raw_reaction_add",
        "on_raw_reaction_remove",
        "on_ready",
        "on_member_join",
        "on_member_remove"
    )

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.events = []
        self.patcher = self._patcher(self.bot)

        for event in self.DEFAULT_EVENTS:
            bot.add_listener(self.default_event_wrapper(event), event)

        self.events.append(self._AutoEmojiReact)
        self._auto_react_to_emojis = False
        self._auto_react_to_emojis_check = lambda m: not m.author.bot

    @property
    def AutoReact(self):
        return self._auto_react_to_emojis

    def AutoReact_setter(self, emoji: Union[str, None], check: Union[Callable] = None):
        self._auto_react_to_emojis = emoji
        if check:
            self._auto_react_to_emojis_check = check

    @AutoReact.setter
    def AutoReact(self, emoji: Union[str, None]):
        self.AutoReact_setter(emoji)

    @EventFunctionWrapper(events=["on_message"], pass_self=True)
    async def _AutoEmojiReact(self, message: discord.Message):
        if self._auto_react_to_emojis and self._auto_react_to_emojis_check(message):
            await message.add_reaction(self._auto_react_to_emojis)

    async def default_event(self, event_type, *args, **kwargs):
        for event in self.events:
            if event_type in event.wait_for_events:
                local = locals()
                call_with = [event.tag_resolver[tag](local) if tag else None for tag in event.tags]
                await event(*call_with, *args, **kwargs)

    def default_event_wrapper(self, event_type):
        async def func(*args, **kwargs):
            await self.default_event(event_type, *args, **kwargs)

        return func

    def EmojiReact(self, **kwargs) -> _EmojiReact:
        return _EmojiReact(self, **kwargs)

    def EmojiReactRoler(self, **kwargs) -> _EmojiReactRoler:
        return _EmojiReactRoler(self, **kwargs)

    class _patcher:
        def __init__(self, bot):
            self.bot = bot

        def patch_ctx(self):
            commands.Context = CustomContext

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.toolbox = None
        tb = kwargs.get('toolbox', None)
        kwargs.pop('toolbox', None)
        super().__init__(*args, **kwargs)
        if tb:
            self.AttachToolbox()

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

    def MakeToolbox(self):
        return toolbox(self)

    def AttachToolbox(self):
        self.toolbox = self.MakeToolbox()