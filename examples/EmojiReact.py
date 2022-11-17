from dpy_toolbox import Bot
import discord
import asyncio

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)
TOKEN = ''  # BAD

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

# callback get called on add/remove of emoji
async def emoji_callback(react: bot.toolbox.EmojiReact, message: discord.Message, payload: discord.RawReactionActionEvent):
    user: discord.User = await bot.fetch_user_from_cache(payload.user_id)
    await message.reply(f'{user.mention} you {"reacted with" if payload.event_type == "REACTION_ADD" else "removed your reaction"} {payload.emoji.name}')

@bot.command()
async def emoji_react(ctx, *, message=None):
    if not message:
        return
    msg = await ctx.send(message)
    # new emoji react
    s = bot.toolbox.EmojiReact()
    # add emojis and their callback func
    s.add("✅", emoji_callback)
    s.add("❌", emoji_callback)
    # start listing
    await s.listen(msg)
    # stop listening after 10 s
    await asyncio.sleep(10)
    s.abort()

bot.run(TOKEN)