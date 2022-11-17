# -*- coding: utf-8 -*-

import discord

from dpy_toolbox import Bot, CustomContext
from dpy_toolbox.ui.Paginator import Paginator, Book

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD


@bot.command()
async def goread(ctx: CustomContext[Bot]) -> None:
    myBook = Book.from_iter(["Hello", "Yellow", "Fellow"])
    myView = Paginator(myBook, show_page=True)
    await ctx.send_paginator(myView)


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

bot.run(TOKEN)
