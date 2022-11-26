# -*- coding: utf-8 -*-

import asyncio

import discord
from discord import app_commands

from dpy_toolbox import Bot, translating

bot = Bot(command_prefix='!', intents=discord.Intents.all(), auto_sync=True)
TOKEN = ''  # BAD

# language: command name: ...
TRANSLATION_TABLE = {
    "hey": {
        "default": "en",
        "en": {
            "name": "hello",
            "description": "say hello"
        },
        "de": {
            "name": "hallo",
            "description": "sage hallo"
        },
    },
    "add": {
        "en": {
            "name": "add",
            "params": {
                "number1": {
                    "name": "first_number",
                },
            }
        },
        "de": {
            "name": "addieren",
            "description": "addiere zwei nummern",
            "params": {
                "number1": {
                    "name": "erste_number",
                },
                "number2": {
                    "name": "zweite_nummer",
                    "description": "die zweite nummer"
                }
            }
        }
    }
}


@bot.tree.command()
async def hey(inter: discord.Interaction) -> None:
    await inter.response.send_message(f"Hello {inter.user.mention}!")


"""
in this example no default lang is set therefore the 
    if there is no translation for
        the command's name the function name (here "add") will be used
        the command's description the by discord.py provided default ("...") will be used
        a command's param the description defined using the describe decorator will be used
"""


@bot.tree.command()
@app_commands.describe(number1="the first number", number2="the second number")
async def add(inter: discord.Interaction, number1: int, number2: int) -> None:
    await inter.response.send_message(f"The solution is: `{number1 + number2}`!")


@bot.event
async def on_ready() -> None:
    print(f'Running as {bot.user}')

if __name__ == '__main__':
    asyncio.run(bot.tree.set_translator(translating.DictonaryTranslator(TRANSLATION_TABLE)))
    bot.run(TOKEN)
