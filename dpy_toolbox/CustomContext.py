from typing import Union, Optional, Callable, Any, Iterable
import discord
from discord.ext import commands
import asyncio

class CustomContext(commands.Context):
    async def ask(
            self,
            question: Union[str, discord.Embed, None] = None,
            check: Callable = None,
            timeout: int = 120,
            delQuestion: bool = True,
            delAnswer: bool = True
    ) -> Union[Optional[str], Any]:
        """
        Simply ask a user a question using `bot.wait_for`

        :param str question: Will send a text-message before waiting for a response
        :param discord.Embed question: Will send an embed before waiting for a response
        :param None question: Will not send any message before waiting
        :param check: The check that will be used for the response | f(message)
        :param int timeout: The timeout of the response
        :param bool delQuestion: Will delete the question if provided and true
        :param bool delAnswer: Will delete the user's answer if true
        :return: The user's response message
        :rtype: discord.Message

        :raises asyncio.TimeoutError: If the user doesnt answer within the timeout
        """

        if question:
            match_question = {
                str: "content",
                discord.Embed: "embed"
            }
            question = await self.send(**{match_question[type(question)]: question})
        if not check:
            check = lambda m: m.author == self.author and m.channel == self.channel

        reply = None
        try:
            reply = await self.bot.wait_for("message", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            pass

        if delQuestion:
            await question.delete()

        if not reply:
            return None

        if delAnswer:
            await reply.delete()

        return reply

    async def send_view(self, view, *args, **kwargs):
        m = await self.send(view=view, *args, **kwargs)
        setattr(view, "message", m)

    async def send_paginator(self, view):
        page = view.book.pages[0].content
        table = {
            discord.Embed: "embed",
            str: "content"
        }
        m = await self.send(**{table[type(page)]: page}, view=view)
        setattr(view, "message", m)

    async def delete(self, delay: Optional[float] = None):
        await self.message.delete(delay=delay)

    async def respond(self, *args, **kwargs):
        await self.reply(*args, **kwargs)