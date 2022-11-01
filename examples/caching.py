from discord.ext import commands
from dpy_toolbox import Bot
import discord

TOKEN = ''  # BAD
LOG_CHANNEL_ID = "880934899622740072"
PREFIX = '!'

bot = Bot(command_prefix=PREFIX, intents=discord.Intents.all())

@bot.command()
async def fetch_channel(ctx: commands.Context, channel: discord.TextChannel):
    log_channel = await bot.get_channel_from_cache(channel.id)
    await log_channel.send(f"{ctx.author} ({ctx.author.id}) used hello in {ctx.channel.mention}")

@bot.command()
async def fetch_role(ctx: commands.Context, role: discord.Role):
    role = await bot.get_role_from_cache(ctx.guild.id, role.id)
    await ctx.send(f"fetched {role.mention}!")

@bot.command()
async def fetch_guild(ctx: commands.Context, guild_id: int):
    guild = await bot.get_guild_from_cache(guild_id)
    await ctx.send(f"fetched {guild}!")

@bot.command()
async def fetch_user(ctx: commands.Context, member: discord.Member):
    user = await bot.fetch_user_from_cache(member.id)
    await ctx.send(f"fetched {user.mention}!")

@bot.command()
async def fetch_member(ctx: commands.Context, member: discord.Member):
    cached_member = await bot.get_member_from_cache(ctx.guild.id, member.id)
    await ctx.send(f"fetched {cached_member.mention}!")

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

@bot.event
async def on_message(msg: discord.Message):
    # logging example
    # this will not send a new request if the channel has been fetched previously
    # => prevents rate limits due to fetching
    # => speeds up bot
    if msg.content.startswith(PREFIX):  # check if message starts with command prefix
        command = msg.content.lstrip(PREFIX).split()[0]  # get command name
        if command in bot.all_commands: # check if command is registered
            log_channel = await bot.get_channel_from_cache(LOG_CHANNEL_ID)  # get log channel
            await log_channel.send(
                f"{msg.author} ({msg.author.id}) used {command} in {msg.channel.mention}"
            )
    await bot.process_commands(msg)

bot.run(TOKEN)