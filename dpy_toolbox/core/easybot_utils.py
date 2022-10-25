from typing import Union
from discord.ext import commands
from ..core import try_exc
import discord
import inspect

class MessageResponse:
    def __init__(self, message: discord.Message):
        self.type = None
        self.message = message

    async def autocomplete(self, *args, **kwargs):
        pass

    async def defer(self, *args, **kwargs):
        pass

    async def edit_message(self, *args, **kwargs):
        return await self.message.edit(*args, **kwargs)

    def is_done(self, *args, **kwargs):
        return False

    async def pong(self, *args, **kwargs):
        return True

    async def send_message(self, *args, **kwargs):
        return await self.message.channel.send(*args, **kwargs)

    async def send_modal(self, *args, **kwargs):
        pass

class InteractionMessageReference:
    def __init__(self, ref: Union[discord.Interaction, discord.Message]):
        self._is_interaction = False
        if isinstance(ref, discord.Interaction):
            self._is_interaction = True
            members = {i[0]: i[1] for i in inspect.getmembers(ref)}
            for k, v in members.items():
                try_exc(setattr, self, k, v)
        else:
            # Classes
            self.message = ref
            self.response = MessageResponse(self.message)

            # Base Variables
            self.id = self.message.id
            self.user = self.message.author
            self.created_at = self.message.created_at
            self.command_failed = False

            self.channel = self.message.channel
            self.channel_id = self.channel.id

            self.guild = self.message.guild
            self.guild_id = self.guild.id

    # Overwritten if interaction:
    async def delete_original_response(self, *args, **kwargs):
        return await self.message.edit(*args, **kwargs)

    async def edit_original_response(self, *args, **kwargs):
        return await self.message.edit(*args, **kwargs)

    async def original_response(self, *args, **kwargs):
        return await self.message

    # Wont be overwritten
    async def send(self, *args, **kwargs):
        """
        Send a message to the channel or respond to the interaction
        """
        if self._is_interaction:
            return await self.response.send_message(*args, **kwargs)
        return await self.message.channel.send(*args, **kwargs)

    async def reply(self, *args, **kwargs):
        """
        Reply to the message or interaction
        """
        if self._is_interaction:
            return await self.response.send_message(*args,**kwargs)
        return await self.message.reply(*args, **kwargs)

async def send_message(ref: Union[discord.Message, discord.Interaction], *content, **kwargs):
    if isinstance(ref, discord.Interaction):
        ref: discord.Interaction
        return await ref.response.send_message(*content, **kwargs)
    ref: discord.Message
    return await ref.channel.send(*content, **kwargs)

async def send_reply(ref: Union[discord.Message, discord.Interaction], *content, **kwargs):
    if isinstance(ref, discord.Interaction):
        ref: discord.Interaction
        return await ref.response.send_message(*content, **kwargs)
    ref: discord.Message
    return await ref.reply(*content, **kwargs)