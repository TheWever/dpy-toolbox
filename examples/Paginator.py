from dpy_toolbox import Paginator, Book
from dpy_toolbox import Bot
import discord

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD

@bot.command()
async def goread(ctx):
    myBook = Book.from_iter(["Hello", "Yellow", "Fellow"])
    print(myBook)
    myView = Paginator(myBook)
    await ctx.send_paginator(myView)

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

if __name__ == '__main__':
    bot.run(TOKEN)