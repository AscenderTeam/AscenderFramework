# Client Proxy

Ascender Framework exposes a high-level `ClientProxy` class for communicating with other services.
A proxy instance is tied to a transport registered via `provideMicroservices` and is retrieved through
dependency injection using the token you configured.

## Injecting a proxy

```python title="src/controllers/cache.py"
from typing import Annotated

from ascender.core import Controller, Inject
from ascender.common.microservices import ClientProxy

@Controller()
class CacheController:
    def __init__(
        self,
        redis_proxy: Annotated[ClientProxy, Inject("REDIS_TRANSPORT")],
    ) -> None:
        self.redis = redis_proxy
```

With the proxy injected, you can interact with other microservices:

- `emit` – emit an event pattern without waiting for acknowledgement.
- `send` – send a message pattern and wait for the response.

```python
await self.redis.emit("cache.updated", payload)
result = await self.redis.send("users.get", response_type=list[UserResponse])
```
