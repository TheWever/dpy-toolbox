import asyncio
from typing import Union, Callable, Optional
from discord.ext import commands
from discord.types.snowflake import Snowflake
import discord
from .sink import to_SinkVoiceClient, MP3Sink, SinkVoiceClient, SinkVoiceChannel, to_SinkVoiceChannel, VirtualSink

from .core import (
    EventFunctionWrapper,
    AnyGuildChannel,
    MessageFilter,
    await_any,
    set_multikey_dict_item,
    get_multikey_dict_item
)

from .ui import *
from .CustomContext import CustomContext
from .EmojiReact import EmojiReact as _EmojiReact
from .EmojiReact import EmojiReactRoler as _EmojiReactRoler

__all__ = (
    "Toolbox",
    "Bot",
    "ButtonReact",
    "ButtonReactRoler",
    "ButtonDisplay",
    "to_SinkVoiceClient",
    "SinkVoiceClient",
    "MP3Sink",
    "SinkVoiceChannel",
    "to_SinkVoiceChannel",
    "QuestioningModal",
    "SingleQuestion",
    "VirtualSink",
    "MessageFilter"
)

class Toolbox:
    DEFAULT_EVENTS = (
        "on_message",
        "on_raw_reaction_add",
        "on_raw_reaction_remove"
    )

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.events = []
        self.listen_for_messages = {}
        self.patcher = self._patcher(self.bot)

        for event in self.DEFAULT_EVENTS:
            bot.add_listener(self.default_event_wrapper(event), event)

        self.events.append(self._AutoEmojiReact)
        self.events.append(self._MessageFilterInvoker)
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
    async def _MessageFilterInvoker(self, message: discord.Message):
        for m in self.listen_for_messages.values():
            if m["filter"](message):
                await m["cb"](message)

    async def add_message_callback(
            self,
            name: str,
            callback: Callable,
            message_filter: MessageFilter = None,
            overwrite_existing: bool = False
    ):
        """
        Automatically invokes your function upon receiving a message that matches your filter
        :param overwrite_existing: If the existing command should be overwritten
        :param str name: The name of your action
        :param Callable callback: The function that will be invoked
        :param MessageFilter message_filter: The filter that decides on which messages to invoke your function
        """
        if name in self.listen_for_messages and not overwrite_existing:
            raise TypeError(f"Name `{name}` already assigned to existing command!")
        self.listen_for_messages[name] = {"cb": callback, "filter": message_filter}

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
        self.toolbox: Optional[Toolbox] = None
        self.is_synced = False
        self.auto_sync: bool = kwargs.pop('auto_sync', False)

        tb: Union[bool, int] = kwargs.pop('toolbox', False)
        super().__init__(*args, **kwargs)
        if tb:
            self.AttachToolbox()
        if self.auto_sync:
            self.add_listener(self._autosync, "on_ready")

    async def getch_user(self, user_id: Union[str, int]) -> discord.User:
        return self.get_user(user_id) or await self.fetch_user(user_id)

    async def getch_channel(self, channel_id: Union[str, int]) -> AnyGuildChannel:
        return self.get_channel(channel_id) or await self.fetch_channel(channel_id)

    async def getch_guild(self, guild_id: Union[str, int]) -> discord.Guild:
        return self.get_guild(guild_id) or await self.fetch_guild(guild_id)

    async def getch_role(self, guild_id: Union[str, int, discord.Guild], role_id: Union[str, int]) -> discord.Role:
        guild: discord.Guild = guild_id
        if not isinstance(guild_id, discord.Guild):
            guild = await self.getch_guild(int(guild_id))
        return guild.get_role(role_id) or list(filter(lambda role: role.id == int(role_id), await guild.fetch_roles()))

    async def getch_member(self, guild_id: Union[str, int, discord.Guild], user_id: Union[str, int]) -> discord.Role:
        guild: discord.Guild = guild_id
        if not isinstance(guild_id, discord.Guild):
            guild = await self.getch_guild(int(guild_id))
        return guild.get_member(user_id) or await guild.fetch_member(user_id)

    async def _autosync(self):
        await self.sync(self.auto_sync if isinstance(self.auto_sync, int) else None)
        self.remove_listener(self._autosync, "on_ready")

    async def sync(self, guild: Union[Snowflake, int] = None, bypass: bool = False):
        if not self.is_synced or bypass:
            self.is_synced = True
            if isinstance(guild, int):
                guild = self.get_guild(guild)
            await self.tree.sync(guild=guild)

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

    def MakeToolbox(self) -> Toolbox:
        return Toolbox(self)

    def AttachToolbox(self):
        self.toolbox = self.MakeToolbox()
