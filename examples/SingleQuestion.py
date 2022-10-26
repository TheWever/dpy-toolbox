from dpy_toolbox import Bot
from dpy_toolbox.ui import SingleQuestion
import discord

TOKEN = ''  # BAD

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)

@bot.tree.command()
async def rateme(inter: discord.Interaction):
    modal = SingleQuestion(
        "Rate me 1 / 10",
        callback=lambda self, inter: inter.response.send_message(f"Thank you for rating me! (`{self.result} / 10`)")
    )
    await inter.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

bot.run(TOKEN)