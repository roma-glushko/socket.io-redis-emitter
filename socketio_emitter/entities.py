from pydantic import BaseModel, Field

from typing import Tuple, Dict, Any, List, Optional

import msgpack

from socketio_emitter.consts import ROOT_NAMESPACE, PacketTypes

EventName = str
MessageData = Tuple[EventName, Dict[str, Any]]


class MessageFlags(BaseModel):
    """
    Volatile:
        Sets a modifier for a subsequent event emission that the event data may be lost
        if the client is not ready to receive messages (because of network slowness or other issues,
        or because they’re connected through long polling
        and is in the middle of a request-response cycle).
    Compress:
        Sets the compress flag.
    """
    volatile: bool = False
    compress: bool = False


class MessageOptions(BaseModel):
    rooms: Optional[List[str]] = None
    flags: Optional[MessageFlags] = None
    except_rooms: Optional[List[str]] = Field(None, alias="except")

    class Config:
        allow_population_by_field_name = True


class Packet(BaseModel):
    data: MessageData
    type: PacketTypes = PacketTypes.REGULAR
    namespace: str = Field(ROOT_NAMESPACE, alias="nsp")

    class Config:
        allow_population_by_field_name = True


class Message(BaseModel):
    emitter_id: str
    packet: Packet
    options: MessageOptions

    def raw(self) -> bytes:
        """
        Generates a serialized version of a Socket.IO emit message
        Returns:
            Raw/Serialized Socket.IO emit message
        """
        return msgpack.packb(
            (
                self.emitter_id,
                self.packet.dict(by_alias=True),
                self.options.dict(by_alias=True),
            )
        )
