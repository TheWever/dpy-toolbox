from typing import Union, Annotated
from discord.ext import commands
import discord

__all__ = (
    "AnyChannel",
    "AnyGuildChannel",
    "AnyMessageReference"
)

AnyGuildChannel = Union[
    discord.TextChannel,
    discord.VoiceChannel,
    discord.StageChannel,
    discord.CategoryChannel,
    discord.ForumChannel
]

AnyChannel = Union[
    discord.DMChannel,
    AnyGuildChannel
]

AnyMessageReference = Union[
    discord.Interaction,
    discord.Message,
    commands.Context
]
