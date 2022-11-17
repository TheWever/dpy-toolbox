# -*- coding: utf-8 -*-

import discord

from dpy_toolbox.ui import SingleQuestion
from dpy_toolbox import Bot

TOKEN = ''  # BAD

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)


async def callback(self, inter: discord.Interaction) -> None:
    await inter.response.send_message(f"Thank you for rating me! (`{self.result} / 10`)")


@bot.tree.command()
async def rateme(inter: discord.Interaction) -> None:
    modal = SingleQuestion(
        "Rate me 1 / 10",
        callback=callback
    )
    await inter.response.send_modal(modal)


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

bot.run(TOKEN)
