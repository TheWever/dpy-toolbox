# -*- coding: utf-8 -*-

import discord

from dpy_toolbox import Bot, CustomContext

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD


@bot.command()
async def ask_age(ctx: CustomContext[Bot]) -> None:
    r = await ctx.ask("Whats your age?", del_answer=False, del_question=False)
    await r.reply(f"You are {r.content} years old!")


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

if __name__ == '__main__':
    bot.run(TOKEN)
