import asyncio
import discord
from typing import Optional, Union, Callable, Coroutine, Any, Tuple, Dict
from discord.ext import commands
from discord import app_commands, Message, Interaction
from discord.ext.commands import Bot
from discord.types.snowflake import Snowflake
from .bot import Bot, toolbox
from .core import MessageFilter, EventFunction, EventFunctionWrapper, BaseFilter, tokenize
from .core.easybot_utils import send_message, send_reply, InteractionMessageReference

DEFAULT_EVENT_ARG_FORMATTER = {
    "on_message": (InteractionMessageReference, )
}

class SimpleTrigger:
    def __init__(self, event, check):
        self.event = event
        self.check = check

    async def __call__(self, *args, **kwargs):
        return await self.check(*args, **kwargs)

    @classmethod
    def on_message(cls, filters: MessageFilter):
        async def callback(message: discord.Message):
            if filters(message):
                return True
            return False
        return cls("on_message", callback)

    @classmethod
    def on_member_join(cls, filters: BaseFilter = None):
        async def callback(member: discord.Member):
            if filters(member):
                return True
            return False

        return cls("on_member_join", callback if filters else None)

    @classmethod
    def on_member_leave(cls, filters: BaseFilter = None):
        async def callback(member: discord.Member):
            if filters(member):
                return True
            return False

        return cls("on_member_remove", callback if filters else None)

class SimpleAction:
    @staticmethod
    def delete_message(delay: float = None) -> Callable[[Bot, Message | Interaction], Coroutine[Any, Any, None]]:
        """
        Delete the message

        :param float delay: The times it takes for the message to get deleted
        :return Coroutine: The action the command will execute
        """
        async def action(bot: commands.Bot, ref: Union[discord.Message, discord.Interaction]):
            await ref.message.delete(delay=delay)
        return action

    @staticmethod
    def react_to_message(reaction) -> Callable[[Bot, Message | Interaction], Coroutine[Any, Any, None]]:
        """
        React to
        :param reaction:
        :return:
        """
        async def action(bot: commands.Bot, ref: Union[discord.Message, discord.Interaction]):
            await ref.add_reaction(reaction)
        return action

    @staticmethod
    def respond(*response) -> Callable[[Bot, Message | Interaction], Coroutine[Any, Any, None]]:
        async def action(bot: commands.Bot, ref: Union[discord.Message, discord.Interaction]):
            await send_reply(ref, *response)
        return action

    @staticmethod
    def send(*response) -> Callable[[Bot, InteractionMessageReference], Coroutine[Any, Any, None]]:
        async def action(bot: commands.Bot, ref: InteractionMessageReference):
            await ref.send(*response)
        return action

    @staticmethod
    def send_to_channel(channel_id, *response
    ) -> Callable[[Any, tuple[Any, ...], dict[str, Any]], Coroutine[Any, Any, None]]:
        async def action(bot, *args, **kwargs):
            channel = bot.text_channels.get(channel_id, None)
            if not channel:
                channel = await bot.fetch_channel(channel_id)
                bot.text_channels[channel.id] = channel
            kwargs["bot"] = bot
            for arg in args:
                kwargs[arg.__class__.__name__.lower()] = arg
            await channel.send(tokenize(" ".join(response), **kwargs))
        return action

    @staticmethod
    def ask_user(
            *, question: str,
            timeout: float = 360.0, return_content: bool = True
    ) -> Callable[[Bot, Message | Interaction], Coroutine[Any, Any, str | None]]:
        """
        Ask a user and get his response
        :param question: The question you want to ask the user
        :param bool return_content:
        :param float timeout:
        """
        async def action(bot: commands.Bot, ref: Union[discord.Message, discord.Interaction]) -> Optional[str]:
            await send_message(ref, *question)
            try:
                fm = await bot.wait_for('message', timeout=timeout, check=lambda m: m.author.id == ref.author.id and m.channel.id == ref.channel.id)
            except asyncio.TimeoutError:
                return None
            if return_content:
                return fm.content
            return fm
        return action

class EasyBot(Bot):
    EVENT_ARG_FORMATTER = DEFAULT_EVENT_ARG_FORMATTER

    def __init__(self, token: str, command_prefix: str = "!", intents=discord.Intents.all(), **kwargs):
        super().__init__(command_prefix, intents=intents, **kwargs)
        self.token = token
        self.listen_for = {}
        self.AttachToolbox()
        self.toolbox: toolbox
        self.listener = EventFunction(self._SimpleEventListener, [], ("pass_bot", "pass_event"))
        self.add_to_listener = lambda x: self.listener.wait_for_events.append(x)
        self.toolbox.events.append(self.listener)
        self.toolbox.events.append(self._AutoSync)
        self.is_synced = 0
        self.text_channels = {}

    def initialize(self, register_slash=True):
        if not register_slash:
            self.is_synced = 1

        def initialization_wrapper(func):
            func()
            self.run(self.token)
        return initialization_wrapper

    async def register_slash(self, guild_id: Union[str, int, Snowflake] = None):
        await self.tree.sync(guild=guild_id)

    async def sync_slash(self, guild_id: Union[str, int, Snowflake] = None):
        await self.tree.sync(guild=guild_id)

    async def _SimpleEventListener(self, bot, event, *args, **kwargs):
        for ev in self.listen_for.values():
            if ev["event"] == event:
                t = ev.get("trigger", None)
                if t.check and not await t(*args, **kwargs):
                    return
                formatted = args
                formatter = DEFAULT_EVENT_ARG_FORMATTER.get(event, None)
                if formatter:
                    formatted = [formatter[i](v) if formatter else v for i, v in enumerate(args)]
                await ev["action"](bot, *formatted, **kwargs)

    @EventFunctionWrapper(events=["on_ready"], pass_bot=True)
    async def _AutoSync(self):
        if not self.is_synced:
            await self.tree.sync()
            self.is_synced = 1

    def add_simple_action(
            self,
            name: str,
            trigger: Union[str, SimpleTrigger],
            action: Callable = None,
            message_filter: Optional[MessageFilter] = None,
            overwrite_existing: bool = False,
            **kwargs
    ):
        """
        Automatically executes the set action to all messages that match your filter

        :param trigger: The trigger the bot is looking waiting for
        :param overwrite_existing: If the existing command should be overwritten
        :param str name: The name of your action
        :param SimpleAction action: The action you want the bot to perform
        :param MessageFilter message_filter: The filter that decides on which messages to execute given action
        """
        if t := kwargs.pop("trigger_name", None):
            trigger = getattr(SimpleTrigger, t)(**kwargs)
        elif isinstance(trigger, str):
            trigger = SimpleTrigger.on_message(message_filter)
        if name in self.listen_for and not overwrite_existing:
            raise TypeError(f"Name `{name}` already assigned to existing command!")
        if trigger.event not in self.listener.wait_for_events:
            self.add_to_listener(trigger.event)
        self.listen_for[name] = {"trigger": trigger, "action": action, "event": trigger.event}

    def add_simple_response(
            self,
            name: str,
            response: str,
            **kwargs
    ):
        """
        Automatically executes the set action to all messages that match your filter

        :param response: The message the bot will respond with
        :param str name: The name of your action
        """
        if name in self.listen_for:
            raise TypeError(f"Name `{name}` already assigned to existing command!")
        if "on_message" not in self.listener.wait_for_events:
            self.add_to_listener("on_message")
        self.listen_for[name] = {
            "trigger": SimpleTrigger.on_message(MessageFilter(match_content=name, account_type=0)),
            "action": SimpleAction.send(response),
            "event": "on_message"
        }

    def remove_simple_action(self, name: str):
        """
        Deletes a simple action

        :param str name: The name of your action
        """
        del self.listen_for[name]

    def add_simple_slash(
            self,
            name: str,
            action: Callable = None,
            guild_id: Union[Snowflake, str, int] = None,
            **kwargs
    ):
        """
        Adds a simple slash command to your bot

        :param str name: The name of your action
        :param SimpleAction action: The action you want the bot to perform
        """
        @app_commands.command(name=name, **kwargs)
        async def EasyBotCommand(ref):
            await action(InteractionMessageReference(ref))
        if isinstance(guild_id, (str, int)):
            guild_id = self.get_guild(guild_id)
        self.tree.add_command(EasyBotCommand, guild=guild_id)