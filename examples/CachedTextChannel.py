from discord.ext import commands
from dpy_toolbox import Bot
import discord

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD

@bot.command()
async def hello(ctx: commands.Context):
    # dont log like this use on_message
    # this will not send a new request if the channel has been fetched previously
    # => prevents rate limits due to fetching
    log_channel = bot.get_channel_from_cache("880934899622740072")
    await log_channel.send(f"{ctx.author} ({ctx.author.id}) used hello in {ctx.channel.mention}")

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

bot.run(TOKEN)