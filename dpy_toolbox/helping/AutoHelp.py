from discord.ext.commands.bot import BotBase
from typing import Any, Iterable, Optional
from discord.ext import commands
import discord

DEFAULT_HELP: dict[str, Any] = {
    'description': None,
    'params_name': {},
    'params_desc': {},
}

DEFAULT_TRANSLATOR = {
    "not_found": "[any]",
    "required": "[required]",
    "not_required": "[not required]",
    str: "text",
    int: "number",
    discord.Member: "user",
    discord.TextChannel: "text channel",
    discord.VoiceChannel: "voice channel",
    discord.CategoryChannel: "category",
    discord.Role: "role"
}


class AutoHelp(commands.MinimalHelpCommand):
    def __init__(
            self,
            title: str = None,
            description: str = None,
            message_type: int = 2,
            translator: dict[Any, str] = None
    ):
        """
        Add an AutoHelp command to your bot

        :param str title: The embed / message title
        :param str description: The description of your help menu
        :param int message_type: The type of menu
            Message:           1
            Embed:             2
            Embed (no fields): 3
        :param dict translator: The translator used to translate types to str
        """
        super().__init__()
        self.bot: Optional[BotBase] = None
        self.title: str = title or "Help Menu:"
        self.description: str = description or ""
        self.message_type = message_type  # 1: message; 2: embed; 3: embed no fields
        self.translator = translator or DEFAULT_TRANSLATOR

    # to make sure the deepcopy will have all commands available
    def copy(self):
        obj = self.__class__(*self.__original_args__, **self.__original_kwargs__)
        obj._command_impl = self._command_impl
        obj.bot = self.bot
        return obj

    def _add_to_bot(self, bot: commands.bot.BotBase) -> None:
        command = commands.help._HelpCommandImpl(self, **self.command_attrs)
        bot.add_command(command)
        self._command_impl = command
        self.bot = bot

    def make_embed(self, help_for: list[Iterable[str]]):
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=discord.Color.blurple()
        )
        if self.message_type == 3:
            embed.description = "\n".join([f"{x[0]}\n{x[1]}" for x in help_for])
            return embed
        for field in help_for:
            field_name, field_value = field[0], field[1]
            embed.add_field(
                name=field_name,
                value=field_value
            )
        return embed

    def make_message(self, help_for: list[Iterable[str]]):
        return f"**{self.title}**" + "\n" + "\n".join([f"> {x[0]}\n```{x[1]}```" for x in help_for])

    def format_help(self) -> list[Iterable[str]]:
        help_for: list[Iterable[str]] = []
        for command in self.bot.commands:
            if not (h := getattr(command, 'helping', None)):
                continue

            desc = h['description']
            help_for.append((
                f"{command.name}: {', '.join(h['params_name'].get(x, x) for x in command.params)}",  # field name
                (f"{desc}\n{'=' * int(len(desc) * 0.81) }\n" if desc else command.short_doc or '') +  # field value
                f"\n".join(
                    [f"{h['params_name'].get(k, k)} {self.translator.get(v, None) or self.translator.get('not_found', 'any')} "
                     f"{self.translator.get('required', 'required') if v.required else self.translator.get('not_required', 'not required')}"
                     f"\n{h['params_desc'].get(k, '')}" for k, v in command.params.items()])
            ))
        return help_for

    @property
    def sendable(self):
        return {
            "content": self.make_message(self.format_help())
        } if self.message_type == 1 else {
            "embed": self.make_embed(self.format_help())
        }

    async def send_pages(self):
        destination = self.get_destination()
        await destination.send(**self.sendable)

def helpful(*description: str) -> Any:
    def decorator(command: commands.Command):
        if getattr(command, 'helping', None) is None:
            command.helping = DEFAULT_HELP
        command.helping["description"] = " ".join(description)
        return command
    return decorator


def rename(**kwargs: str) -> Any:
    def decorator(command: commands.Command):
        if getattr(command, 'helping', None) is None:
            command.helping = DEFAULT_HELP
        for k, v in kwargs.items():
            command.helping['params_name'][k] = v
        return command
    return decorator


def describe(**kwargs: str) -> Any:
    def decorator(command: commands.Command):
        if getattr(command, 'helping', None) is None:
            command.helping = DEFAULT_HELP
        for k, v in kwargs.items():
            command.helping['params_desc'][k] = v
        return command
    return decorator
