# Context Objects

Handlers decorated with `@MessagePattern` or `@EventPattern` can receive transport
specific metadata through context objects. Use the `Ctx()` marker to access these
details.

```python title="src/controllers/users.py"
from typing import Annotated

from ascender.common.microservices import MessagePattern, Ctx, KafkaContext

class UsersController:
    @MessagePattern("users.get")
    async def get_users(
        self,
        ctx: Annotated[KafkaContext, Ctx()],
    ) -> list[UserResponse]:
        print(ctx.offset, ctx.partition, ctx.correlation_id)
        return []
```

The context type depends on the transport in use (e.g. `KafkaContext`, `RedisContext`).
It provides low-level information such as headers, identifiers, or delivery details
from the underlying message broker.

