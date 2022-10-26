
from __future__ import annotations

import asyncio
from typing import (
    TYPE_CHECKING,
    Callable,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

from discord import utils, VoiceChannel
from discord.errors import ClientException
from discord.voice_client import VoiceClient, VoiceProtocol
from .voice_client import SinkVoiceClient

__all__ = (
    "SinkVoiceChannel",
)

T = TypeVar("T", bound=VoiceProtocol)

if TYPE_CHECKING:
    from datetime import datetime

    from discord.channel import (
        DMChannel,
        GroupChannel,
        PartialMessageable,
        TextChannel,
        VoiceChannel,
    )
    from discord.client import Client
    from discord.state import ConnectionState
    from discord.threads import Thread

    PartialMessageableChannel = Union[TextChannel, VoiceChannel, Thread, DMChannel, PartialMessageable]
    MessageableChannel = Union[PartialMessageableChannel, GroupChannel]
    SnowflakeTime = Union["Snowflake", datetime]

MISSING = utils.MISSING

class Connectable(Protocol):
    """An ABC that details the common operations on a channel that can
    connect to a voice server.
    The following implement this ABC:
    - :class:`~discord.VoiceChannel`
    - :class:`~discord.StageChannel`
    Note
    ----
    This ABC is not decorated with :func:`typing.runtime_checkable`, so will fail :func:`isinstance`/:func:`issubclass`
    checks.
    """

    __slots__ = ()
    _state: ConnectionState

    def _get_voice_client_key(self) -> Tuple[int, str]:
        raise NotImplementedError

    def _get_voice_state_pair(self) -> Tuple[int, int]:
        raise NotImplementedError

    async def connect(
        self,
        *,
        timeout: float = 60.0,
        reconnect: bool = True,
        cls: Callable[[Client, Connectable], T] = VoiceClient,
    ) -> T:
        """|coro|
        Connects to voice and creates a :class:`VoiceClient` to establish
        your connection to the voice server.
        This requires :attr:`Intents.voice_states`.
        Parameters
        -----------
        timeout: :class:`float`
            The timeout in seconds to wait for the voice endpoint.
        reconnect: :class:`bool`
            Whether the bot should automatically attempt
            a reconnect if a part of the handshake fails
            or the gateway goes down.
        cls: Type[:class:`VoiceProtocol`]
            A type that subclasses :class:`~discord.VoiceProtocol` to connect with.
            Defaults to :class:`~discord.VoiceClient`.
        Raises
        -------
        asyncio.TimeoutError
            Could not connect to the voice channel in time.
        ~discord.ClientException
            You are already connected to a voice channel.
        ~discord.opus.OpusNotLoaded
            The opus library has not been loaded.
        Returns
        --------
        :class:`~discord.VoiceProtocol`
            A voice client that is fully connected to the voice server.
        """

        key_id, _ = self._get_voice_client_key()
        state = self._state

        if state._get_voice_client(key_id):
            raise ClientException("Already connected to a voice channel.")

        client = state._get_client()
        voice = cls(client, self)

        if not isinstance(voice, VoiceProtocol):
            raise TypeError("Type must meet VoiceProtocol abstract base class.")

        state._add_voice_client(key_id, voice)

        try:
            await voice.connect(timeout=timeout, reconnect=reconnect)
        except asyncio.TimeoutError:
            try:
                await voice.disconnect(force=True)
            except Exception:
                # we don't care if disconnect failed because connection failed
                pass
            raise  # re-raise

        return

class SinkVoiceChannel(VoiceChannel):
    async def connect(self, *, timeout: float = 60.0, reconnect: bool = True, **kwargs) -> SinkVoiceClient:
        """|coro|
        Connects to voice and creates a :class:`VoiceClient` to establish
        your connection to the voice server.
        This requires :attr:`Intents.voice_states`.
        Parameters
        -----------
        timeout: :class:`float`
            The timeout in seconds to wait for the voice endpoint.
        reconnect: :class:`bool`
            Whether the bot should automatically attempt
            a reconnect if a part of the handshake fails
            or the gateway goes down.
        cls: Type[:class:`VoiceProtocol`]
            A type that subclasses :class:`~discord.VoiceProtocol` to connect with.
            Defaults to :class:`~discord.VoiceClient`.
        Raises
        -------
        asyncio.TimeoutError
            Could not connect to the voice channel in time.
        ~discord.ClientException
            You are already connected to a voice channel.
        ~discord.opus.OpusNotLoaded
            The opus library has not been loaded.
        Returns
        --------
        :class:`~discord.VoiceProtocol`
            A voice client that is fully connected to the voice server.
        """

        key_id, _ = self._get_voice_client_key()
        state = self._state

        if state._get_voice_client(key_id):
            raise ClientException("Already connected to a voice channel.")

        client = state._get_client()
        voice = SinkVoiceClient(client, self)

        if not isinstance(voice, (SinkVoiceClient, VoiceProtocol)):
            raise TypeError("Type must meet VoiceProtocol abstract base class.")

        state._add_voice_client(key_id, voice)

        try:
            await voice.connect(timeout=timeout, reconnect=reconnect)
        except asyncio.TimeoutError:
            try:
                await voice.disconnect(force=True)
            except Exception:
                # we don't care if disconnect failed because connection failed
                pass
            raise  # re-raise
        return voice