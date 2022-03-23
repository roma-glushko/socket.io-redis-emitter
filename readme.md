# Socket.IO Redis Emitter

This is an asynchronous Redis-based [Socket.IO emitter](https://socket.io/docs/v4/emitting-events/) for Python.

## Features

- High quality, typed and modern Python codebase
- Clean, concise and Pythonic API
- Supports namespaces, rooms and regular Socket.IO message emitting

```python
from aioredis import Redis
from socketio_emitter import Emitter

client = Redis(...)
emitter = Emitter(client=client)

with emitter.namespace("/nsp") as nsp:
    with nsp.rooms("room1", "room2") as clients:
        await clients.emit("machineStatus", {"status": "ok"})
```

- Remote requests to join, leave rooms or to disconnect 

```python
from aioredis import Redis
from socketio_emitter import Emitter

client = Redis(...)
emitter = Emitter(client=client)

with emitter.namespace("/nsp") as nsp:
    with nsp.rooms("room1", "room2") as clients:
        await clients.join("room3")
        # await clients.leave("room3")
        # await clients.disconnect()
```