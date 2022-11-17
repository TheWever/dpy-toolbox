import discord
from discord.ext import commands

from dpy_toolbox import Bot, ButtonDisplay, ButtonReact

TOKEN = ''  # BAD

bot = Bot(command_prefix='!', intents=discord.Intents.all())


async def rect_callback(inter: discord.Interaction) -> None:
    await inter.response.send_message(f"{inter.user} interacted with me!")


@bot.command()
async def rect(ctx: commands.Context) -> None:
    myView = ButtonReact()
    myView.add(rect_callback, ButtonDisplay(label="Text"))
    await ctx.send("Hello", view=myView)


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

bot.run(TOKEN)
