# -*- coding: utf-8 -*-

import asyncio

import discord
from discord.ext import commands

from dpy_toolbox import Bot
from dpy_toolbox.EmojiReact import EmojiReact

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)
TOKEN = ''  # BAD


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')


# callback get called on add/remove of emoji
async def emoji_callback(
        react: EmojiReact,
        message: discord.Message,
        payload: discord.RawReactionActionEvent
) -> None:
    user: discord.User = await bot.getch_user(payload.user_id)
    await message.reply(
        f'{user.mention} you {"reacted with" if payload.event_type == "REACTION_ADD" else "removed your reaction"} '
        f'{payload.emoji.name}'
    )


@bot.command()
async def emoji_react(ctx: commands.Context, *, message: str = None) -> None:
    if not message:
        return
    msg = await ctx.send(message)
    # new emoji react
    s = bot.toolbox.emoji_react()
    # add emojis and their callback func
    s.add("✅", emoji_callback)
    s.add("❌", emoji_callback)
    # start listing
    await s.listen(msg)
    # stop listening after 10 s
    await asyncio.sleep(10)
    s.abort()

bot.run(TOKEN)
