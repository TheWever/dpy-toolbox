from dpy_toolbox import Bot
import discord

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD

@bot.command()
async def ask_age(ctx):
    r = await ctx.ask("Whats your age?", delAnswer=False, delQuestion=False)
    await r.reply(f"You are {r.content} years old!")

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

if __name__ == '__main__':
    bot.run(TOKEN)