from typing import Any, Dict, Tuple, cast

import msgpack

RawProtocol = Tuple[str, Dict[str, Any], Dict[str, Any]]


def decode_message(message: bytes) -> RawProtocol:
    return cast(RawProtocol, msgpack.unpackb(message))
