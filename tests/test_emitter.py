from typing import Any, Dict, Tuple
from unittest.mock import AsyncMock

import pytest

from socketio_emitter import (
    DEFAULT_CHANNEL_PREFIX,
    Emitter,
    Message,
    MessageFlags,
    MessageOptions,
    Packet,
    PacketTypes,
)
from tests.conftest import decode_message


@pytest.fixture
def emitter_id() -> str:
    return "test_emitter"


@pytest.fixture
def event() -> str:
    return "testEvent"


@pytest.fixture
def event_data() -> Dict[str, Any]:
    return {"msg": "John joined the workspace"}


@pytest.fixture
def namespace() -> str:
    return "/workspace"


def test_socketio_protocol(
    emitter_id: str, event: str, event_data: Dict[str, Any], namespace: str
) -> None:
    room: str = "12345"
    exc_room: str = "54321"

    message: Message = Message(
        emitter_id=emitter_id,
        packet=Packet(data=(event, event_data), namespace=namespace),
        options=MessageOptions(
            flags=MessageFlags(volatile=True),
            rooms=[room],
            except_rooms=[exc_room],
        ),
    )

    raw_message = decode_message(message.raw())

    assert len(raw_message) == 3

    rcv_emitter_id, rcv_packet, rcv_options = raw_message

    assert rcv_emitter_id == emitter_id

    assert isinstance(rcv_packet, dict), type(rcv_packet)
    assert set(rcv_packet.keys()) == {"data", "type", "nsp"}
    assert rcv_packet.get("nsp") == namespace
    assert rcv_packet.get("type") == PacketTypes.REGULAR

    rcv_message_data = rcv_packet.get("data", ("", {}))

    assert isinstance(rcv_message_data, list)
    assert len(rcv_message_data) == 2

    rcv_event: str
    rcv_data: Dict[str, Any]
    rcv_event, rcv_data = rcv_message_data

    assert rcv_event == event
    assert rcv_data == event_data

    assert isinstance(rcv_options, dict)
    assert set(rcv_options.keys()) == {"flags", "rooms", "except"}


class TestEmitter:
    @staticmethod
    def _get_emitter(emitter_id: str) -> Tuple[Emitter, AsyncMock]:
        redis_mock = AsyncMock()

        return Emitter(redis_mock, emitter_id=emitter_id), redis_mock

    @staticmethod
    def _get_message_from_mock(redis_mock: AsyncMock) -> Tuple[str, Message]:
        (channel_name, decoded_message), _ = list(redis_mock.publish.await_args)
        message: Message = Message.from_raw(*decode_message(decoded_message))

        return channel_name, message

    async def test_event_emitting(
        self, emitter_id: str, event: str, event_data: Dict[str, Any], namespace: str
    ) -> None:
        emitter, redis_mock = self._get_emitter(emitter_id)
        room: str = "124"

        async with emitter.namespace(namespace) as nsp:
            async with nsp.rooms(room):
                await emitter.emit(
                    event=event,
                    data=event_data,
                )

        channel_name, rcv_message = self._get_message_from_mock(redis_mock)

        assert DEFAULT_CHANNEL_PREFIX in channel_name, channel_name
        assert namespace in channel_name, channel_name
        assert room in channel_name, channel_name

        assert rcv_message.emitter_id == emitter_id

        assert rcv_message.packet.type == PacketTypes.REGULAR
        assert rcv_message.packet.namespace == namespace

        rcv_event, rcv_message_data = rcv_message.packet.data

        assert rcv_event == event
        assert rcv_message_data == event_data

        assert rcv_message.options.rooms == [room]

    async def test_emitting_to_all_rooms(
        self, emitter_id: str, namespace: str, event: str, event_data: Dict[str, Any]
    ) -> None:
        emitter, redis_mock = self._get_emitter(emitter_id)

        async with emitter.namespace(namespace) as nsp:
            async with nsp.all_rooms():
                await emitter.emit(
                    event=event,
                    data=event_data,
                )

        _, rcv_message = self._get_message_from_mock(redis_mock)

        assert rcv_message.packet.namespace == namespace
        assert rcv_message.options.rooms is None

    async def test_emitting_to_several_namespaces(
        self, emitter_id: str, event: str, event_data: Dict[str, Any]
    ) -> None:
        emitter, redis_mock = self._get_emitter(emitter_id)

        workspace_namespace: str = "/workspaces"
        org_namespace: str = "/organizations"

        async with emitter.namespace(workspace_namespace) as workspace_nsp:
            async with workspace_nsp.all_rooms():
                await emitter.emit(
                    event=event,
                    data=event_data,
                )

        channel_name, rcv_message = self._get_message_from_mock(redis_mock)

        assert workspace_namespace in channel_name
        assert rcv_message.packet.namespace == workspace_namespace

        async with emitter.namespace(org_namespace) as org_nsp:
            async with org_nsp.all_rooms():
                await emitter.emit(
                    event=event,
                    data=event_data,
                )

        channel_name, rcv_message = self._get_message_from_mock(redis_mock)

        assert org_namespace in channel_name
        assert rcv_message.packet.namespace == org_namespace
