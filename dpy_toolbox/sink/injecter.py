import discord
from .voice_client import VoiceClient
from .gateway import received_message
from . import opus

def inject():
    discord.VoiceClient = VoiceClient
    discord.voice_client.VoiceClient = VoiceClient
    discord.gateway.DiscordVoiceWebSocket.ssrc_map = {}
    discord.gateway.received_message = received_message
    discord.opus = opus
