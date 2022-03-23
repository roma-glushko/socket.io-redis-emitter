import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, Sequence

from aioredis import Redis

from socketio_emitter.consts import (
    CHANNEL_SEPARATOR,
    DEFAULT_CHANNEL_PREFIX,
    DEFAULT_EMITTER_ID,
    ROOT_NAMESPACE,
)
from socketio_emitter.entities import Message, MessageFlags, MessageOptions, Packet

logger = logging.getLogger(__name__)

ALL_ROOMS = None


class Emitter:
    def __init__(
        self,
        client: "Redis",
        *,
        channel_prefix: str = DEFAULT_CHANNEL_PREFIX,
        emitter_id: str = DEFAULT_EMITTER_ID,
    ) -> None:
        """
        Inits an emitter instance
        Args:
            client (Redis): Configured instance of a Redis client
            channel_prefix:
            emitter_id:
        """
        self.channel_prefix = channel_prefix
        self.emitter_id = emitter_id

        self.client = client

        self._namespace: Optional[str] = None
        self._rooms: Optional[Sequence[str]] = None
        self._except_rooms: Optional[Sequence[str]] = None

    @asynccontextmanager
    async def namespace(
        self, name: str = ROOT_NAMESPACE
    ) -> AsyncGenerator["Emitter", None]:
        """
        Select a namespace to braodcast
        Args:
            name (str): Namespace Name
        Returns:
            Self
        """
        previous_namespace = self._namespace
        try:
            self._namespace = name if name.startswith("/") else f"/{name}"
            yield self
        finally:
            self._namespace = previous_namespace

    @asynccontextmanager
    async def all_rooms(
        self, *, except_: Optional[Sequence[str]] = None
    ) -> AsyncGenerator["Emitter", None]:
        """
        Select all rooms in the specified namespace
        Args:
            except_ (List[str]): List of rooms to except from broadcasting
        Returns:
            Self
        """
        previous_rooms = self._rooms
        previous_except_rooms = self._except_rooms

        try:
            self._rooms = ALL_ROOMS
            self._except_rooms = except_

            yield self
        finally:
            self._rooms = previous_rooms
            self._except_rooms = previous_except_rooms

    @asynccontextmanager
    async def rooms(self, *rooms: Sequence[str]) -> AsyncGenerator["Emitter", None]:
        """
        Select specific rooms to broadcast
        Args:
            *rooms: Rooms to select
        Returns:
            Self
        """
        previous_rooms = self._rooms
        try:
            self._rooms = rooms
            yield self
        finally:
            self._rooms = previous_rooms

    async def emit(
        self,
        event: str,
        data: Dict[str, Any],
        volatile: bool = False,
    ) -> None:
        """
        Emits an event with the data to a specified namespace and room(s)
        Args:
            event (str): Event Name
            data (Dict[str, Any]): Exact Message Data
            volatile (bool): Enabled UDP-like behaviur
        Returns:
            None
        """
        message: Message = Message(
            emitter_id=self.emitter_id,
            packet=Packet(data=(event, data), namespace=self._namespace),
            options=MessageOptions(
                flags=MessageFlags(volatile=volatile),
                rooms=self._rooms,
                except_rooms=self._except_rooms,
            ),
        )

        if self._rooms is ALL_ROOMS:
            return await self._emit_message(message, namespace=str(self._namespace))

        for room in self._rooms:
            await self._emit_message(
                message,
                namespace=str(self._namespace),
                room=room,
            )

    async def _emit_message(
        self, message: Message, *, namespace: str, room: Optional[str] = None
    ) -> None:
        """
        Emit a new message to the selected namespace/room
        Args:
            message (Message): Full Emit Message corresponding to Socket.IO protocol
            namespace (str): Namespace
            room (str): Room Name
        Returns:
            None
        """
        channel_name = self._get_emit_channel(namespace, room)

        await self._publish_message(channel_name, message.raw())

    async def _publish_message(self, channel_name: str, message: bytes) -> None:
        """
        Publish a raw message to the broker
        Args:
            channel_name (str): PubSub Channel Name
            message (bytes): Serialized message data
        Returns:
            None
        """
        await self.client.publish(channel_name, message)

    def _get_emit_channel(self, namespace: str, room: Optional[str] = None) -> str:
        channel_parts: List[str] = [self.channel_prefix, namespace]

        if room:
            channel_parts.append(room)

        return CHANNEL_SEPARATOR.join(channel_parts)

    def _get_request_channel(self, namespace: str, room: Optional[str] = None) -> str:
        channel_parts: List[str] = [f"{self.channel_prefix}-request", namespace]

        if room:
            channel_parts.append(room)

        return CHANNEL_SEPARATOR.join(channel_parts)
