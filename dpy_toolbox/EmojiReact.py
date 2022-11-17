import discord
from discord.ext import commands
from .core import EventFunctionWrapper
from typing import Optional, Union, Callable

class EmojiReact:
    def __init__(self, parent, table: Optional[dict] = None):
        self.parent = parent
        self.bot: commands.Bot = parent.bot
        self._table = table if table else {}
        self.callback_funcs = {}
        self._counter = {}
        self._pass_kwargs = {}
        self.messages = []

    def _create_callback(self, message):
        @EventFunctionWrapper(events=["on_raw_reaction_add", "on_raw_reaction_remove"])
        async def callback(payload):
            if payload.emoji.name in self._table and payload.message_id == message.id and payload.member != self.bot.user:
                self._counter[message.id][payload.emoji.name] += 1 if payload.event_type == "REACTION_ADD" else -1
                await self._table[payload.emoji.name](self, message, payload, **self._pass_kwargs[message.id])

        return callback

    def add(self, emoji: Union[str], func: Union[Callable]):
        """
        Add an item to the table that will be used for .listen()

        :param str emoji: The emoji your function will be attached to
        :param Callable func: The function that will be called on addition and removal of the emoji
        """
        self._table[emoji] = func

    def remove(self, emoji: Union[str]):
        """
        Remove the emoji and attached function if registered

        :param str emoji: The bound emoji
        """
        if emoji in self._table:
            self._table.pop(emoji)

    async def listen(self, message: Union[discord.Message], **kwargs):
        """
        Start to listen for reactions on message (will also react with them)

        :param discord.Message message: The message you want to listen to
        """
        self.messages.append(message)
        self._counter[message.id] = {k: 0 for k in self._table}
        self._pass_kwargs[message.id] = kwargs
        f = self._create_callback(message)
        self.callback_funcs[message.id] = f
        self.parent.events.append(f)

        for k in self._table:
            await message.add_reaction(k)

    def abort(self, message: Union[None, discord.Message, int] = None):
        """
        Stop listening for all reactions on attached messages

        :param discord.Message message: The message you want to stop listing to
        """
        messages = [getattr(message, "id", message)]
        if not message:
            messages = list(self.messages)

        for msg in messages:
            self.messages.remove(msg)
            f = self.callback_funcs.pop(msg.id)
            self.parent.events.remove(f)
            self._counter.pop(msg.id)
            self._pass_kwargs.pop(msg.id)

    def get_emoji_count(self, message: Union[discord.Message, int]):
        message_id = getattr(message, "id", message)
        return self._counter[message_id]

# dont inherit (had to rewrite whole class)
class EmojiReactRoler:
    def __init__(self, parent, table: Optional[dict] = None):
        self.parent = parent
        self.bot: commands.Bot = parent.bot
        self._table = table if table else {}
        self.callback_funcs = []

    def _create_callback(self, message_id):
        @EventFunctionWrapper(events=["on_raw_reaction_add", "on_raw_reaction_remove"], pass_bot=True)
        async def callback(bot, payload):
            if payload.message_id == message_id and payload.emoji.name in self._table:
                if payload.event_type == "REACTION_ADD" and payload.member != self.bot.user:
                    await payload.member.add_roles(*self._table[payload.emoji.name][0])
                elif self._table[payload.emoji.name][1]:
                    guild = bot.get_guild(payload.guild_id)
                    member = discord.utils.get(guild.members, id=payload.user_id)

                    await member.remove_roles(*self._table[payload.emoji.name][0])

        return callback

    async def add(self, emoji: Union[str], role: Union[discord.Role, list[discord.Role]], remove_role: Union[bool] = True) -> None:
        """
        Add an emoji to the table followed by the role(s) the user should receive

        :param emoji: The emoji that the role will be attached to
        :param role: The role(s) you want to add to the user upon reacting
        :param remove_role: If the user should get his role removed upon removing his reaction
        """
        self._table[emoji] = [[role] if isinstance(role, discord.Role) else role, [remove_role]]

    async def remove(self, emoji: Union[str]) -> None:
        """
        Remove an emoji and attached role(s)

        :param str emoji: The bound emoji
        """
        if emoji in self._table:
            self._table.pop(emoji)

    async def listen(self, message: Union[discord.Message]) -> None:
        """
        Start to listen for reactions on message (will also react with them)

        :param discord.Message message:
        """
        for k in self._table:
            await message.add_reaction(k)
        f = self._create_callback(message.id)
        self.callback_funcs.append(f)
        self.parent.events.append(f)

    async def abort(self) -> None:
        """
        Stop listening for all reactions on attached messages
        """
        for f in self.callback_funcs:
            self.callback_funcs.remove(f)
            self.parent.events.remove(f)
