from dpy_toolbox import Bot
import discord

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    bot.toolbox.AutoReact_setter("✅", lambda m: m.author == bot.user)

bot.run(TOKEN)