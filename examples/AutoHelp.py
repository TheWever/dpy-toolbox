from dpy_toolbox import helping, Bot
import discord

TOKEN = ''  # BAD

bot = Bot(
    command_prefix='!',
    intents=discord.Intents.all(),
    help_command=helping.AutoHelp(
        title='Help menu:',
        description="Just a simple help menu..."
    ),
    toolbox=True
)

'''
How the help menu will look like:

Help Menu:                          - title
Just a simple help menu...          - description

add: first addend, second addend    - command + params
This command will sum two numbers   - description
==========================          
first addend [any] [required]       - param 1 + type + is required ?
=> Just a number                    - param 1 description
second addend [any] [required]      - param 2 + type + is required ?
=> Just another number              - param 2 description
'''
# put these decorators ABOVE the command
@helping.helpful(
    "This command will sum two numbers"  # description of your command
)
@helping.rename(
    number_1="first addend",             # new name of param named number_1
    number_2="second addend"             # new name of param named number_1
)
@helping.describe(
    number_1="=> Just a number",         # description of param named number_1
    number_2="=> Just another number"    # description of param named number_1
)
@bot.command()
async def add(ctx, number_1: int, number_2: int):
    print(number_1 + number_2)
    await ctx.channel.send(f"sum: {number_1 + number_2}")

bot.run(TOKEN)