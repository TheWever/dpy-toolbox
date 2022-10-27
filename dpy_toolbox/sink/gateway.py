"""
py-cord
    IDENTIFY            = 0
    SELECT_PROTOCOL     = 1
    READY               = 2
    HEARTBEAT           = 3
    SESSION_DESCRIPTION = 4
    SPEAKING            = 5
    HEARTBEAT_ACK       = 6
    RESUME              = 7
    HELLO               = 8
    RESUMED             = 9
    CLIENT_CONNECT      = 12
    CLIENT_DISCONNECT   = 13

d.py
    DISPATCH           = 0
    HEARTBEAT          = 1
    IDENTIFY           = 2
    PRESENCE           = 3
    VOICE_STATE        = 4
    VOICE_PING         = 5
    RESUME             = 6
    RECONNECT          = 7
    REQUEST_MEMBERS    = 8
    INVALIDATE_SESSION = 9
    HELLO              = 10
    HEARTBEAT_ACK      = 11
    GUILD_SYNC         = 12
"""

import logging
import aiohttp
import asyncio
from discord.voice_client import VoiceKeepAliveHandler
from discord import utils, ConnectionClosed, DiscordException
from typing import Any
import threading
from discord.enums import SpeakingState
import struct
_log = logging.getLogger(__name__)

class WebSocketClosure(DiscordException):
    pass

class DiscordSinkWebSocket:
    """Implements the websocket protocol for handling voice connections.
    Attributes
    -----------
    IDENTIFY
        Send only. Starts a new voice session.
    SELECT_PROTOCOL
        Send only. Tells discord what encryption mode and how to connect for voice.
    READY
        Receive only. Tells the websocket that the initial connection has completed.
    HEARTBEAT
        Send only. Keeps your websocket connection alive.
    SESSION_DESCRIPTION
        Receive only. Gives you the secret key required for voice.
    SPEAKING
        Send only. Notifies the client if you are currently speaking.
    HEARTBEAT_ACK
        Receive only. Tells you your heartbeat has been acknowledged.
    RESUME
        Sent only. Tells the client to resume its session.
    HELLO
        Receive only. Tells you that your websocket connection was acknowledged.
    RESUMED
        Sent only. Tells you that your RESUME request has succeeded.
    CLIENT_CONNECT
        Indicates a user has connected to voice.
    CLIENT_DISCONNECT
        Receive only.  Indicates a user has disconnected from voice.
    """

    IDENTIFY            = 0
    SELECT_PROTOCOL     = 1
    READY               = 2
    HEARTBEAT           = 3
    SESSION_DESCRIPTION = 4
    SPEAKING            = 5
    HEARTBEAT_ACK       = 6
    RESUME              = 7
    HELLO               = 8
    RESUMED             = 9
    CLIENT_CONNECT      = 12
    CLIENT_DISCONNECT   = 13

    def __init__(self, socket, loop, *, hook=None):
        self.ws = socket
        self.loop = loop
        self._keep_alive = None
        self._close_code = None
        self.secret_key = None
        self.ssrc_map = {}
        if hook:
            self._hook = hook

    async def _hook(self, *args):
        pass

    async def send_as_json(self, data):
        _log.debug('Sending voice websocket frame: %s.', data)
        await self.ws.send_str(utils._to_json(data))

    send_heartbeat = send_as_json

    async def resume(self):
        state = self._connection
        payload = {
            'op': self.RESUME,
            'd': {
                'token': state.token,
                'server_id': str(state.server_id),
                'session_id': state.session_id
            }
        }
        await self.send_as_json(payload)

    async def identify(self):
        state = self._connection
        payload = {
            'op': self.IDENTIFY,
            'd': {
                'server_id': str(state.server_id),
                'user_id': str(state.user.id),
                'session_id': state.session_id,
                'token': state.token
            }
        }
        await self.send_as_json(payload)

    @classmethod
    async def from_client(cls, client, *, resume=False, hook=None):
        """Creates a voice websocket for the :class:`VoiceClient`."""
        gateway = 'wss://' + client.endpoint + '/?v=4'
        http = client._state.http
        socket = await http.ws_connect(gateway, compress=15)
        ws = cls(socket, loop=client.loop, hook=hook)
        ws.gateway = gateway
        ws._connection = client
        ws._max_heartbeat_timeout = 60.0
        ws.thread_id = threading.get_ident()

        if resume:
            await ws.resume()
        else:
            await ws.identify()

        return ws

    async def select_protocol(self, ip, port, mode):
        payload = {
            'op': self.SELECT_PROTOCOL,
            'd': {
                'protocol': 'udp',
                'data': {
                    'address': ip,
                    'port': port,
                    'mode': mode
                }
            }
        }

        await self.send_as_json(payload)

    async def client_connect(self):
        payload = {
            'op': self.CLIENT_CONNECT,
            'd': {
                'audio_ssrc': self._connection.ssrc
            }
        }

        await self.send_as_json(payload)

    async def speak(self, state=SpeakingState.voice):
        payload = {
            'op': self.SPEAKING,
            'd': {
                'speaking': int(state),
                'delay': 0
            }
        }

        await self.send_as_json(payload)

    async def received_message(self, msg):
        _log.debug('Voice websocket frame received: %s', msg)
        op = msg['op']
        data = msg.get('d')

        if op == self.READY:
            await self.initial_connection(data)
        elif op == self.HEARTBEAT_ACK:
            self._keep_alive.ack()
        elif op == self.RESUMED:
            _log.info('Voice RESUME succeeded.')
        elif op == self.SESSION_DESCRIPTION:
            self._connection.mode = data['mode']
            await self.load_secret_key(data)
        elif op == self.HELLO:
            interval = data['heartbeat_interval'] / 1000.0
            self._keep_alive = VoiceKeepAliveHandler(ws=self, interval=min(interval, 5.0))
            self._keep_alive.start()

        elif op == self.SPEAKING:
            ssrc = data['ssrc']
            user = int(data['user_id'])
            speaking = data['speaking']
            if ssrc in self.ssrc_map:
                self.ssrc_map[ssrc]['speaking'] = speaking
            else:
                self.ssrc_map.update({ssrc: {'user_id': user, 'speaking': speaking}})

        await self._hook(self, msg)

    async def initial_connection(self, data):
        state = self._connection
        state.ssrc = data['ssrc']
        state.voice_port = data['port']
        state.endpoint_ip = data['ip']

        packet = bytearray(70)
        struct.pack_into('>H', packet, 0, 1) # 1 = Send
        struct.pack_into('>H', packet, 2, 70) # 70 = Length
        struct.pack_into('>I', packet, 4, state.ssrc)
        state.socket.sendto(packet, (state.endpoint_ip, state.voice_port))
        recv = await self.loop.sock_recv(state.socket, 70)
        _log.debug('received packet in initial_connection: %s', recv)

        # the ip is ascii starting at the 4th byte and ending at the first null
        ip_start = 4
        ip_end = recv.index(0, ip_start)
        state.ip = recv[ip_start:ip_end].decode('ascii')

        state.port = struct.unpack_from('>H', recv, len(recv) - 2)[0]
        _log.debug('detected ip: %s port: %s', state.ip, state.port)

        # there *should* always be at least one supported mode (xsalsa20_poly1305)
        modes = [mode for mode in data['modes'] if mode in self._connection.supported_modes]
        _log.debug('received supported encryption modes: %s', ", ".join(modes))

        mode = modes[0]
        await self.select_protocol(state.ip, state.port, mode)
        _log.info('selected the voice protocol for use (%s)', mode)

    @property
    def latency(self):
        """:class:`float`: Latency between a HEARTBEAT and its HEARTBEAT_ACK in seconds."""
        heartbeat = self._keep_alive
        return float('inf') if heartbeat is None else heartbeat.latency

    @property
    def average_latency(self):
        """:class:`list`: Average of last 20 HEARTBEAT latencies."""
        heartbeat = self._keep_alive
        if heartbeat is None or not heartbeat.recent_ack_latencies:
            return float('inf')

        return sum(heartbeat.recent_ack_latencies) / len(heartbeat.recent_ack_latencies)

    async def load_secret_key(self, data):
        _log.info('received secret key for voice connection')
        self.secret_key = self._connection.secret_key = data.get('secret_key')
        await self.speak()
        await self.speak(False)

    async def poll_event(self):
        # This exception is handled up the chain
        msg = await asyncio.wait_for(self.ws.receive(), timeout=30.0)
        if msg.type is aiohttp.WSMsgType.TEXT:
            await self.received_message(utils._from_json(msg.data))
        elif msg.type is aiohttp.WSMsgType.ERROR:
            _log.debug('Received %s', msg)
            raise ConnectionClosed(self.ws, shard_id=None) from msg.data
        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING):
            _log.debug('Received %s', msg)
            raise ConnectionClosed(self.ws, shard_id=None, code=self._close_code)

    async def close(self, code=1000):
        if self._keep_alive is not None:
            self._keep_alive.stop()

        self._close_code = code
        await self.ws.close(code=code)
