from .voice_client import SinkVoiceClient
from .gateway import DiscordSinkWebSocket
from . import opus
from discord import VoiceClient
from .sink import Sink, VirtualSink, UnvirtualSink
from .encodings import MP3Sink
from .base import SinkVoiceChannel
import discord
import types

async def to_SinkVoiceClient(voice: VoiceClient) -> SinkVoiceClient:
    #vars
    voice.ws = DiscordSinkWebSocket(voice.ws, voice.socket, hook=getattr(voice, '_hook', None))
    voice.decoder = None
    voice.paused = False
    voice.recording = False
    voice.user_timestamps = {}
    voice.sink = None
    voice.starting_time = None
    voice.stopping_time = None

    # static methods
    setattr(voice, 'strip_header_ext', SinkVoiceClient.strip_header_ext)

    # methods
    setattr(voice, 'listen', types.MethodType(SinkVoiceClient.listen, voice))
    setattr(voice, 'stop_listening', types.MethodType(SinkVoiceClient.stop_listening, voice))
    setattr(voice, 'toggle_pause', types.MethodType(SinkVoiceClient.toggle_pause, voice))

    setattr(voice, 'empty_socket', types.MethodType(SinkVoiceClient.empty_socket, voice))
    setattr(voice, 'get_ssrc', types.MethodType(SinkVoiceClient.get_ssrc, voice))

    setattr(voice, 'recv_audio', types.MethodType(SinkVoiceClient.recv_audio, voice))
    setattr(voice, 'recv_decoded_audio', types.MethodType(SinkVoiceClient.recv_decoded_audio, voice))
    setattr(voice, 'unpack_audio', types.MethodType(SinkVoiceClient.unpack_audio, voice))
    setattr(voice, '_get_voice_packet', types.MethodType(SinkVoiceClient._get_voice_packet, voice))

    # En/Decrypt
    setattr(voice, '_decrypt_xsalsa20_poly1305_lite', types.MethodType(SinkVoiceClient._decrypt_xsalsa20_poly1305_lite, voice))
    setattr(voice, '_encrypt_xsalsa20_poly1305_suffix',types.MethodType(SinkVoiceClient._decrypt_xsalsa20_poly1305_lite, voice))
    setattr(voice, '_decrypt_xsalsa20_poly1305_lite', types.MethodType(SinkVoiceClient._decrypt_xsalsa20_poly1305_lite, voice))
    setattr(voice, '_decrypt_xsalsa20_poly1305_lite', types.MethodType(SinkVoiceClient._decrypt_xsalsa20_poly1305_lite, voice))
    setattr(voice, '_decrypt_xsalsa20_poly1305', types.MethodType(SinkVoiceClient._decrypt_xsalsa20_poly1305_lite, voice))
    setattr(voice, '_decrypt_xsalsa20_poly1305_suffix', types.MethodType(SinkVoiceClient._decrypt_xsalsa20_poly1305_lite, voice))

    return voice

async def to_SinkVoiceChannel(channel: discord.VoiceChannel) -> SinkVoiceChannel:
    data = {
        "id": channel.id,
        "name": channel.name,
        "flags": None,
        "bitrate": channel.bitrate,
        "position": channel.position,
        "user_limit": channel.user_limit,
        "rtc_region": channel.rtc_region,
        "overwrites": channel._overwrites,
        "category_id": channel.category_id,
        "last_message_id": channel.last_message_id,
        "video_quality_mode": channel.video_quality_mode,

    }
    vc = SinkVoiceChannel(state=channel._state, guild=channel.guild, data=data)
    """
    #vc.guild = channel.guild
    vc.name = channel.name
    vc.rtc_region = channel.rtc_region
    vc.video_quality_mode = channel.video_quality_mode
    vc.category_id = channel.category_id
    vc.last_message_id = channel.last_message_id
    vc.position = channel.position
    vc.bitrate = channel.bitrate
    vc.user_limit = channel.user_limit
    vc.flags = channel.flags
    vc._overwrites = channel._overwrites
    """
    return vc