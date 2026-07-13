"""
WebSocket listener for the Decent.app (ReaPrime) gateway.

The gateway pushes live telemetry over several WebSocket channels
(machine snapshots, shot settings, water levels, scale snapshots and
device state). This module maintains one long-lived connection per
subscribed channel and reconnects automatically with backoff.

API specification:
https://github.com/tadelv/reaprime/blob/main/assets/api/websocket_v1.yml
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from typing import TYPE_CHECKING, Any

import aiohttp

from custom_components.decent_app.const import LOGGER

if TYPE_CHECKING:
    from collections.abc import Callable

RECONNECT_DELAY_INITIAL_SECONDS = 2.0
RECONNECT_DELAY_MAX_SECONDS = 60.0
HEARTBEAT_SECONDS = 30.0

type MessageHandler = Callable[[dict[str, Any]], None]


class DecentAppWebsocketListener:
    """
    Maintains WebSocket subscriptions to the Decent.app gateway.

    One background task is spawned per subscribed channel. Each task keeps
    the socket open, decodes incoming JSON frames and forwards them to the
    registered handler. Connections are re-established automatically with
    exponential backoff; a handler never sees connection errors.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        """
        Initialize the listener.

        Args:
            base_url: WebSocket base URL of the gateway (ws://host:port).
            session: The aiohttp ClientSession used for connections.

        """
        self._base_url = base_url
        self._session = session
        self._handlers: dict[str, MessageHandler] = {}
        self._tasks: list[asyncio.Task] = []
        self._closed = False

    def subscribe(self, channel: str, handler: MessageHandler) -> None:
        """
        Register a handler for a channel.

        Must be called before async_start(). The handler is invoked in the
        event loop with the decoded JSON object of every received frame.

        Args:
            channel: Channel path relative to the base URL, e.g.
                "ws/v1/machine/snapshot".
            handler: Callback receiving each decoded message.

        """
        self._handlers[channel] = handler

    def async_start(self) -> None:
        """Start one listener task per subscribed channel."""
        loop = asyncio.get_running_loop()
        for channel, handler in self._handlers.items():
            self._tasks.append(loop.create_task(self._listen(channel, handler)))

    async def async_stop(self) -> None:
        """Cancel all listener tasks and wait for them to finish."""
        self._closed = True
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self._tasks.clear()

    async def _listen(self, channel: str, handler: MessageHandler) -> None:
        """Connect to a channel and dispatch messages, reconnecting forever."""
        url = f"{self._base_url}/{channel}"
        delay = RECONNECT_DELAY_INITIAL_SECONDS

        while not self._closed:
            try:
                async with self._session.ws_connect(url, heartbeat=HEARTBEAT_SECONDS) as ws:
                    LOGGER.debug("Connected to WebSocket channel %s", url)
                    delay = RECONNECT_DELAY_INITIAL_SECONDS
                    async for message in ws:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            self._dispatch(channel, handler, message.data)
                        elif message.type in (
                            aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            break
            except (aiohttp.ClientError, OSError, TimeoutError) as exception:
                LOGGER.debug("WebSocket channel %s error: %s", channel, exception)

            if self._closed:
                return
            LOGGER.debug("WebSocket channel %s disconnected, retrying in %.0fs", channel, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, RECONNECT_DELAY_MAX_SECONDS)

    def _dispatch(self, channel: str, handler: MessageHandler, raw: str) -> None:
        """Decode a frame and hand it to the channel handler."""
        try:
            payload = json.loads(raw)
        except ValueError:
            LOGGER.debug("Ignoring non-JSON frame on %s: %.100s", channel, raw)
            return
        if not isinstance(payload, dict):
            return
        try:
            handler(payload)
        except Exception:  # noqa: BLE001 - a faulty handler must not kill the listener task
            LOGGER.exception("Error handling message on channel %s", channel)
