import asyncio

import discord

from dpy_toolbox import Bot
from dpy_toolbox.EmojiReact import EmojiReact

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)
TOKEN = ''  # BAD


def poll_embed(question, upvotes, downvotes) -> discord.Embed:
    return discord.Embed(
        title=f"Question: {question}",
        description=f"{upvotes} people upvoted! {downvotes} people have downvoted!",
        color=discord.Color.green()
    )


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')


# callback get called on add/remove of emoji
async def emoji_callback(
        react: EmojiReact,
        message: discord.Message,
        payload: discord.RawReactionActionEvent,
        question: str
) -> None:
    await message.edit(embed=poll_embed(question, *[react.get_emoji_count(message.id)[x] for x in "✅❌"]))


@bot.command()
async def poll(ctx, duration: int, *, question: str) -> None:
    msg = await ctx.send(embed=poll_embed(question, 0, 0))
    # new emoji react
    s = bot.toolbox.emoji_react()
    # add emojis and their callback func
    s.add("✅", emoji_callback)
    s.add("❌", emoji_callback)
    # start listing
    await s.listen(msg, question=question)
    # stop listening after 10 s
    await asyncio.sleep(duration)
    s.abort()


bot.run(TOKEN)
