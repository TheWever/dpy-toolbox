from discord.ext import commands
from dpy_toolbox import Bot
import discord

TOKEN = ''  # BAD
LOG_CHANNEL_ID = "880934899622740072"
OWNER_ID = "784735765514158090"
PREFIX = '!'

bot = Bot(command_prefix=PREFIX, intents=discord.Intents.all())

@bot.command()
async def fetch_channel(ctx: commands.Context, channel: discord.TextChannel):
    log_channel = await bot.getch_channel(channel.id)
    await log_channel.send(f"{ctx.author} ({ctx.author.id}) used hello in {ctx.channel.mention}")

@bot.command()
async def fetch_role(ctx: commands.Context, role: discord.Role):
    role = await bot.getch_role(ctx.guild.id, role.id)
    await ctx.send(f"fetched {role.mention}!")

@bot.command()
async def fetch_guild(ctx: commands.Context, guild_id: int):
    guild = await bot.getch_guild(guild_id)
    await ctx.send(f"fetched {guild}!")

@bot.command()
async def fetch_user(ctx: commands.Context, member: discord.Member):
    user = await bot.getch_user(member.id)
    await ctx.send(f"fetched {user.mention}!")

@bot.command()
async def fetch_member(ctx: commands.Context, member: discord.Member):
    cached_member = await bot.getch_member(ctx.guild.id, member.id)
    await ctx.send(f"fetched {cached_member.mention}!")

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')
    # ensures that a channel will be returned
    channel = await bot.getch_channel(LOG_CHANNEL_ID)
    await channel.send("Im online!")

@bot.event
async def on_message(msg: discord.Message):
    # logging example
    # this will not send a new request and ensures that a user object will be returned
    # => prevents rate limits due to fetching
    # => speeds up bot
    if msg.content.startswith(PREFIX):                   # check if message starts with command prefix
        command = msg.content.lstrip(PREFIX).split()[0]  # get command name
        if command in bot.all_commands:                  # check if command is registered
            owner = await bot.getch_user(OWNER_ID)       # get log channel
            await owner.send(
                f"{msg.author} ({msg.author.id}) used {command} in {msg.channel.mention}"
            )
    await bot.process_commands(msg)

bot.run(TOKEN)