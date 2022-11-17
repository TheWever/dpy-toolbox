# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from dpy_toolbox import Bot, permissions

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD


@bot.command()
@permissions.is_user(784735765514158090, 837501363927646248)
async def greet(ctx: commands.Context, *, name: str = "John") -> None:
    await ctx.send(f"Hello, {name}!")


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

bot.run(TOKEN)
