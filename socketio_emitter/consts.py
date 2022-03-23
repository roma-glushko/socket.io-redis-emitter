from enum import Enum, unique
from typing import Final, FrozenSet

ROOT_NAMESPACE: Final[str] = "/"

DEFAULT_EMITTER_ID: Final[str] = "emitter"
DEFAULT_CHANNEL_PREFIX: Final[str] = "socket.io"

CHANNEL_SEPARATOR: Final[str] = "#"

RESERVED_EVENTS: FrozenSet[str] = frozenset(
    [
        "connect",
        "connect_error",
        "disconnect",
        "disconnecting",
        "newListener",
        "removeListener",
    ]
)


@unique
class PacketTypes(int, Enum):
    REGULAR = 2
    BINARY = 5


@unique
class RequestTypes(int, Enum):
    pass
