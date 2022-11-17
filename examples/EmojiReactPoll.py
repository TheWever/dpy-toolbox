from dpy_toolbox import Bot
import discord
import asyncio

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)
TOKEN = ''  # BAD
POLL_EMBED = lambda question, upvotes, downvotes: discord.Embed(
    title=f"Question: {question}",
    description=f"{upvotes} people upvoted! {downvotes} people have downvoted!",
    color=discord.Color.green()
)


@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

# callback get called on add/remove of emoji
async def emoji_callback(react: bot.toolbox.EmojiReact, message: discord.Message, payload: discord.RawReactionActionEvent, question):
    await message.edit(embed=POLL_EMBED(question, *[react.get_emoji_count(message.id)[x] for x in "✅❌"]))


@bot.command()
async def poll(ctx, duration: int, *, question):
    msg = await ctx.send(embed=POLL_EMBED(question, 0, 0))
    # new emoji react
    s = bot.toolbox.EmojiReact()
    # add emojis and their callback func
    s.add("✅", emoji_callback)
    s.add("❌", emoji_callback)
    # start listing
    await s.listen(msg, question=question)
    # stop listening after 10 s
    await asyncio.sleep(duration)
    s.abort()


bot.run(TOKEN)