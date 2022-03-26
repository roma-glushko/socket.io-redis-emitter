from typing import Dict, Any, Tuple

import msgpack


def decode_message(message: bytes) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    return msgpack.unpackb(message)