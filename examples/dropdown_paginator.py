# -*- coding: utf-8 -*-

import discord

from dpy_toolbox import Bot, CustomContext
from dpy_toolbox.ui.Paginator import Book, DropdownPaginator, SelectPage

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD


async def btn_callback(inter: discord.Interaction) -> None:
    await inter.response.send_message(f"Hello {inter.user.mention}!")


@bot.command()
async def goread(ctx: CustomContext[Bot]) -> None:
    btn = discord.ui.Button(label="Hello")
    btn.callback = btn_callback
    pages = [
        SelectPage("Hello", "Hello"),
        SelectPage("Yellow", "Yellow", buttons=btn),
        SelectPage(discord.Embed(description="Fellow", color=discord.Color.red()), "Fellow")
    ]
    myBook = Book(pages)
    myView = DropdownPaginator(myBook, ctx.author)
    await ctx.send_paginator(myView)
    # await ctx.send("Here goes text", view=myView) # also works


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

bot.run(TOKEN)
