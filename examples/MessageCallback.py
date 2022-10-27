from dpy_toolbox import Bot, MessageFilter
import discord

bot = Bot(command_prefix='!', intents=discord.Intents.all(), toolbox=True)
TOKEN = ''  # BAD

async def msg_cb_ex(message: discord.Message):
    await message.reply(f"Hi {message.author}, I'm dad!")

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

    await bot.toolbox.add_message_callback(
        "my_command_name",
        msg_cb_ex,
        MessageFilter(
            startswith_content=("Hi", "hi")
        )
    )

bot.run(TOKEN)