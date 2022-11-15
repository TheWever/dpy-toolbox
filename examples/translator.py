from discord import app_commands
from dpy_toolbox import Bot, translating
import discord
import asyncio

bot = Bot(command_prefix='!', intents=discord.Intents.all(), auto_sync=True)
TOKEN = ''  # BAD

# put these above the bot.tree.command()
@translating.default_language("en")                             # set a default language if there is no translation
@translating.translate_command("en", "hello")                   # if lang startswith "en" (true if lang is english) command name = hello
@translating.translate_command("de", "hallo")                   # if lang de command name hallo
@translating.translate_command_description("en", "say hello")   # if lang en (english) command description = say hello
@translating.translate_command_description("de", "sage hallo")  # if lang de command description ) = sage hallo
@bot.tree.command()
async def hey(inter: discord.Interaction):
    await inter.response.send_message(f"Hello {inter.user.mention}!")


"""
in this example no default lang is set therefore the 
    if there is no translation for
        the command's name the function name (here "add") will be used
        the command's description the by discord.py provided default ("...") will be used
        a command's param the description defined using the describe decorator will be used
"""
@translating.translate_polyglot(de="addieren", en="add")                                     # k = lang; v = command name /
@translating.translate_params_name("en", number1="first_number")                             # if lang enlish name of param number1 = "first_number" and param number2 default (here "the second name") will be used
@translating.translate_params_name("de", number1="erste_nummer", number2="zweite_nummer")    # if lang de name of param number1 = "first_number" and param number3 = "second_number"
@translating.translate_params_description("de", number2="die zweite nummer")                 # if lang de description of param number1 = (using describe decorator set description) "the first number" used param number2 = "die zweite nummber"
@translating.translate_command_description("de", "addiere zwei nummern")                     # if lang de description of command = "addiere zwei nummern" else d.py default "..." will be used
@bot.tree.command()
@app_commands.describe(number1="the first number", number2="the second number")
async def add(inter: discord.Interaction, number1: int, number2: int):
    await inter.response.send_message(f"The solution is: `{number1 + number2}`!")

@bot.event
async def on_ready():
    print(f'Running as {bot.user}')

if __name__ == '__main__':
    asyncio.run(bot.tree.set_translator(translating.CommandTranslator()))
    bot.run(TOKEN)