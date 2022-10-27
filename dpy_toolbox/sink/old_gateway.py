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
from discord.voice_client import VoiceKeepAliveHandler, ReconnectWebSocket
from discord import utils, ConnectionClosed, DiscordException
from typing import Any
_log = logging.getLogger(__name__)

class WebSocketClosure(DiscordException):
    pass

async def received_message(self, msg: Any, /) -> None:
    if type(msg) is bytes:
        self._buffer.extend(msg)

        if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
            return
        msg = self._zlib.decompress(self._buffer)
        msg = msg.decode('utf-8')
        self._buffer = bytearray()

    self.log_receive(msg)
    msg = utils._from_json(msg)

    _log.debug('For Shard ID %s: WebSocket Event: %s', self.shard_id, msg)
    event = msg.get('t')
    print(event)
    if event:
        self._dispatch('socket_event_type', event)

    op = msg.get('op')
    data = msg.get('d')
    seq = msg.get('s')
    print(op, self.SPEAKING, op == self.SPEAKING)
    if seq is not None:
        self.sequence = seq

    if self._keep_alive:
        self._keep_alive.tick()

    if op != self.DISPATCH:
        if op == self.RECONNECT:
            # "reconnect" can only be handled by the Client
            # so we terminate our connection and raise an
            # internal exception signalling to reconnect.
            _log.debug('Received RECONNECT opcode.')
            await self.close()
            raise ReconnectWebSocket(self.shard_id)

        if op == self.HEARTBEAT:
            if self._keep_alive:
                beat = self._keep_alive.get_payload()
                await self.send_as_json(beat)
            return

        if op == self.READY:
            await self.initial_connection(data)

        elif op == self.HEARTBEAT_ACK:
            if self._keep_alive:
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
            print(ssrc, user, speaking)
            if ssrc in self.ssrc_map:
                self.ssrc_map[ssrc]['speaking'] = speaking
            else:
                self.ssrc_map.update({ssrc: {'user_id': user, 'speaking': speaking}})
            return

        elif op == self.INVALIDATE_SESSION:
            if data is True:
                await self.close()
                raise ReconnectWebSocket(self.shard_id)

            self.sequence = None
            self.session_id = None
            _log.info('Shard ID %s session has been invalidated.', self.shard_id)
            await self.close(code=1000)
            raise ReconnectWebSocket(self.shard_id, resume=False)

        _log.warning('Unknown OP code %s.', op)
        return

    if event == 'READY':
        self.sequence = msg['s']
        self.session_id = data['session_id']
        _log.info('Shard ID %s has connected to Gateway (Session ID: %s).', self.shard_id, self.session_id)

    elif event == 'RESUMED':
        # pass back the shard ID to the resumed handler
        data['__shard_id__'] = self.shard_id
        _log.info('Shard ID %s has successfully RESUMED session %s.', self.shard_id, self.session_id)

    try:
        func = self._discord_parsers[event]
    except KeyError:
        _log.debug('Unknown event %s.', event)
    else:
        func(data)

    # remove the dispatched listeners
    removed = []
    for index, entry in enumerate(self._dispatch_listeners):
        if entry.event != event:
            continue

        future = entry.future
        if future.cancelled():
            removed.append(index)
            continue

        try:
            valid = entry.predicate(data)
        except Exception as exc:
            future.set_exception(exc)
            removed.append(index)
        else:
            if valid:
                ret = data if entry.result is None else entry.result(data)
                future.set_result(ret)
                removed.append(index)

    for index in reversed(removed):
        del self._dispatch_listeners[index]

async def poll_event(self):
    """Polls for a DISPATCH event and handles the general gateway loop.
    Raises
    ------
    ConnectionClosed
        The websocket connection was terminated for unhandled reasons.
    """
    try:
        msg = await self.socket.receive(timeout=self._max_heartbeat_timeout)
        print(msg.type)
        if msg.type is aiohttp.WSMsgType.TEXT:
            await self.received_message(msg.data)
        elif msg.type is aiohttp.WSMsgType.BINARY:
            await self.received_message(msg.data)
        elif msg.type is aiohttp.WSMsgType.ERROR:
            _log.debug('Received %s', msg)
            raise msg.data
        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSE):
            _log.debug('Received %s', msg)
            raise WebSocketClosure
    except (asyncio.TimeoutError, WebSocketClosure) as e:
        # Ensure the keep alive handler is closed
        if self._keep_alive:
            self._keep_alive.stop()
            self._keep_alive = None

        if isinstance(e, asyncio.TimeoutError):
            _log.info('Timed out receiving packet. Attempting a reconnect.')
            raise ReconnectWebSocket(self.shard_id) from None

        code = self._close_code or self.socket.close_code
        if self._can_handle_close():
            _log.info('Websocket closed with %s, attempting a reconnect.', code)
            raise ReconnectWebSocket(self.shard_id) from None
        else:
            _log.info('Websocket closed with %s, cannot reconnect.', code)
            raise ConnectionClosed(self.socket, shard_id=self.shard_id, code=code) from None
