# Socket.IO Redis Emitter

This is an asynchronous Redis-based [Socket.IO emitter](https://socket.io/docs/v4/emitting-events/) for Python.

## Installation

```bash
pip install socket.io-redis-emitter
# or
poetry add socket.io-redis-emitter
```

## Features

- High quality, typed and modern Python codebase
- Clean, concise and Pythonic API
- Uses [hiredis](https://aioredis.readthedocs.io/en/latest/) as a Redis client
- Supports namespaces, rooms and regular Socket.IO message emitting

```python
import redis
from socketio_emitter import Emitter

client = redis.Redis(...)
emitter = Emitter(client=client)

async with emitter.namespace("/nsp") as nsp:
    async with nsp.rooms("room1", "room2") as clients:
        await clients.emit("machineStatus", {"status": "ok"})
```

- Remote requests to join, leave rooms or to disconnect

```python
import redis
from socketio_emitter import Emitter

client = redis.Redis(...)
emitter = Emitter(client=client)

async with emitter.namespace("/nsp") as nsp:
    async with nsp.rooms("room1", "room2") as clients:
        await clients.join("room3")
        # await clients.leave("room3")
        # await clients.disconnect()
```
