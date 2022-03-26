from typing import Dict, Any, Union

from socketio_emitter import Message, Packet, MessageOptions, MessageFlags, PacketTypes
from tests.conftest import decode_message


def test_socketio_protocol() -> None:
    emitter_id: str = "test_emitter"
    event: str = "testEvent"
    data: Dict[str, Any] = {"msg": "John joined the workspace"}
    namespace: str = "/workspace"
    room: str = "12345"
    exc_room: str = "54321"

    message: Message = Message(
        emitter_id=emitter_id,
        packet=Packet(data=(event, data), namespace=namespace),
        options=MessageOptions(
            flags=MessageFlags(volatile=True),
            rooms=[room],
            except_rooms=[exc_room],
        )
    )

    raw_message = decode_message(message.raw())

    assert len(raw_message) == 3

    rcv_emitter_id, rcv_packet, rcv_options = raw_message

    assert rcv_emitter_id == emitter_id

    assert isinstance(rcv_packet, dict), type(rcv_packet)
    assert set(rcv_packet.keys()) == {"data", "type", "nsp"}
    assert rcv_packet.get("nsp") == namespace
    assert rcv_packet.get("type") == PacketTypes.REGULAR

    rcv_packet = rcv_packet.get("data")

    assert isinstance(rcv_packet, list)
    assert len(rcv_packet) == 2

    rcv_event, rcv_data = rcv_packet

    assert rcv_event == event
    assert rcv_data == data

    assert isinstance(rcv_options, dict)
    assert set(rcv_options.keys()) == {"flags", "rooms", "except"}

