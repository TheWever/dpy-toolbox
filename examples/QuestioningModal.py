from dpy_toolbox import Bot
from dpy_toolbox.ui import QuestioningModal
import discord

TOKEN = ''  # BAD

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)

@bot.tree.command()
async def apply(inter: discord.Interaction):
    async def callback(self: QuestioningModal, inter: discord.Interaction):
        await inter.response.send_message("Application sent!", ephemeral=True)
        embed = discord.Embed(
            title="Application",
            description="Your application has been sent to the staff team!"
        )
        for q, a in self.result.items():
            embed.add_field(name=q, value=a, inline=False)
        await inter.user.send(embed=embed)
        embed.description = f"`{self.values[1]}` application received!"
        await inter.guild.owner.send(embed=embed)

    modal = QuestioningModal(
        "Application",
        q1 = "What is your name",
        q2 = "What is your age",
        q3 = "What do you want to apply for?",
        lengths={"q1": 30, "q2": 2, "q3": 20},
        styles={"q2": discord.TextStyle.short},
        callback=callback
    )
    await inter.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

bot.run(TOKEN)