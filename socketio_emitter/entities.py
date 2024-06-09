from typing import Any, Dict, List, Optional, Sequence, Tuple

import msgpack
from pydantic import BaseModel, ConfigDict, Field

from socketio_emitter.consts import ROOT_NAMESPACE, PacketTypes, RequestTypes

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

    model_config = ConfigDict(populate_by_name=True)


class Packet(BaseModel):
    data: MessageData
    type: PacketTypes = PacketTypes.REGULAR
    namespace: str = Field(ROOT_NAMESPACE, alias="nsp")

    model_config = ConfigDict(populate_by_name=True)


class Message(BaseModel):
    emitter_id: str
    packet: Packet
    options: MessageOptions

    @classmethod
    def from_raw(
        cls, emitter_id: str, packet: Dict[str, Any], options: Dict[str, Any]
    ) -> "Message":
        return cls(
            emitter_id=emitter_id,
            packet=Packet(**packet),
            options=MessageOptions(**options),
        )

    def raw(self) -> bytes:
        """
        Generates a serialized version of a Socket.IO emit message
        Returns:
            Raw/Serialized Socket.IO emit message
        """
        return bytes(
            msgpack.packb(
                (
                    self.emitter_id,
                    self.packet.model_dump(by_alias=True),
                    self.options.model_dump(by_alias=True),
                )
            )
        )


class RequestOptions(BaseModel):
    rooms: Optional[Sequence[str]] = None
    except_rooms: Optional[Sequence[str]] = Field(None, alias="except")

    model_config = ConfigDict(populate_by_name=True)


class RoomRequest(BaseModel):
    type: RequestTypes
    rooms: Sequence[str]
    options: RequestOptions = Field(..., alias="opts")

    model_config = ConfigDict(populate_by_name=True)


class DisconnectRequest(BaseModel):
    type: RequestTypes = RequestTypes.DISCONNECT
    close: bool
    options: RequestOptions = Field(..., alias="opts")

    model_config = ConfigDict(populate_by_name=True)
