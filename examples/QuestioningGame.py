from discord.ext.commands import CommandNotFound
from dpy_toolbox import Bot, CustomContext
import traceback
import discord

bot = Bot(command_prefix='$', intents=discord.Intents.all())
TOKEN = ''  # BAD

questions: dict[str, dict[str, tuple[str, ...]]] = {
    "general": {
        "What year did the Titanic sink in the Atlantic Ocean on 15 April, on its maiden voyage from Southampton?": ("1912",),
        "What is the title of the first ever Carry On film made and released in 1958?": ("carry on sergeant",),
        "What is the name of the biggest technology company in South Korea?": ("samsung",),
    }
}

playing_prefix = "$g"

@bot.command()
async def play(ctx, game: str = None):
    qs = questions.get(game, None)
    if not qs:
        await ctx.send(f"There is no game called {game}...\nYou may choose one of these options:\n{', '.join(questions)}")
        return
    total_q = len(qs)
    total_c = 0

    # q = question; a = answer(s)
    for i, qa in enumerate(qs.items()):
        q, a = qa[0], qa[1]

        embed_q = discord.Embed(
            title=f'Question {i + 1}/{total_q}: {q}',
            description=f'Type {playing_prefix} to make your guess',
            color=discord.Color.blue()
        )

        r = await ctx.ask(
            embed_q,
            delAnswer=False,
            delQuestion=False,
            check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.startswith(playing_prefix)
        )
        if not r:
            await r.channel.send(embed=discord.Embed(
                title=f'Timed out',
                description=f'The game has been ended. Please answer each question within 2 minutes!',
                color=discord.Color.red()
            ))
            return
        correct = r.content.lower().lstrip(playing_prefix).lstrip(" ") in a
        if correct: total_c += 1

        await r.channel.send(embed=discord.Embed(
            title=f'Question {i + 1}: You are {"correct" if correct else "wrong"}',
            description=f'Question: {q}\nThe correct answer/s were: {"/".join(a)}',
            color=discord.Color.green() if correct else discord.Color.red()
        ))

    await ctx.channel.send(embed=discord.Embed(
        title=f'Completed {game}!',
        description=f'You correctly answered {total_c} out of {total_q} questions!',
        color=discord.Color.green()
    ))

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

@bot.event
async def on_command_error(ctx: CustomContext, error: discord.DiscordException):
    # this is the guess prefix; therefore dont print warning; only required if playing prefix startswith bot prefix
    if isinstance(error, CommandNotFound) and ctx.invoked_with == "g":
        return
    traceback.print_exc()

bot.run(TOKEN)