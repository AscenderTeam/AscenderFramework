# Getting Started

## Installation
By default, the module is already included into Ascender Framework, all you have to do is to install required driver for specific transport you want to use.

If you want to use all transports Ascender Framework Microservices can provide then install framework with extras:

```bash
$ poetry add ascender-framework[microservices]
```

This will install all required packages: `aiokafka`, `redis`, `aiopika` and others.

## Getting started
To instantiate the microservice module, use `provideMicroservice()` factory provider method in your bootstrap or application module:
```python title="src/bootstrap.py"
from ascender.common.microservices import Transports, provideMicroservices
from ascender.core.types import IBootstrap


appBootstrap: IBootstrap = {
    "providers": [
        ...,
        provideMicroservices([
            {
                "token": "main",
                "options": {
                    "transport": Transports.TCP,
                    "options": {}
                }
            }
        ])
    ]
}
```
Arguments of list in `provideMicroservices`

| `token`     | An injection token, which will be used to inject `ClientProxy` objects into your controller or elsewhere. Make sure to make it unique and avoid conflicting with existing injection tokens |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `transport` | Specifies transporter to supply microservice with. (for example `Transports.KAFKA`)                                                                                                       |
| `options`   | Transporter specific options, that will be applied to the transport under which it will be defined. (for example `{"bootstrap_servers": "localhost"}`)                                    |

!!! warning
    Be careful when naming `token`. It may conflict with existing injection tokens which may result an unexpected behaviour of Ascneder Framework's Dependency Injection


## Event Patterns & Event-Driven Messaging
Ascender Framework's Microservices recognize messages and events by specific patterns, which can be plain text or any literal object. This allows for both event patterns (event-driven messaging) and message patterns (request-response messaging).

Event-driven messaging enables services to react to events without waiting for direct responses. This approach helps in designing decoupled and scalable systems, where different microservices can emit and subscribe to events asynchronously. This approach helps in designing decoupled and scalable systems, where different microservices can emit and subscribe to events asynchronously.

**Key Characteristics of Event-Driven Messaging:**
- **Asynchronous communication**: Services do not need to wait for a response.
- **Decoupled architecture**: Emitters and listeners operate independently.
- **Scalability**: Multiple subscribers can process events concurrently.
- **Reliability**: Events can be persisted and retried in case of failures.

To create event handler that listens for specific pattern and waits for consuming side to receive message matching this pattern you can use `@EventPattern()` decorator in your controller:
```python
from ascender.core import Controller, Get
from ascender.common.microservices import EventPattern

from dummy.user import UserResponse

@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(self):
        self.users = []
    
    @Get()
    async def main_endpoint(self):
        return "..."
    
    @EventPattern("user.created")
    async def user_created_event(self, data: UserResponse):
        # Do some user specific logic for user creation (e.g. save user into cache or something else)
        self.users.append(data) # WARN: avoid writing shared states in real project or use locks. This one is made for demonstration purposes only!
```

Now each time consumer receives message by `user.created` pattern, it will be detected and `user_created_event` will be executed with data passed there.

## Message Patterns & Request-Response Messaging

The request-response message style is useful when you need to exchange messages between various external services. This paradigm ensures that the service has actually received the message (without requiring you to manually implement an acknowledgment protocol).


**Key Characteristics of Request-Response Messaging:**
- **Synchronous or asynchronous**: Requests can be handled immediately or queued for processing.
- **Guaranteed delivery**: Ensures that a response is received, making it useful for critical operations.
- **Direct communication**: Unlike event-driven messaging, the sender expects a response from the recipient.
- **Fault tolerance**: Allows services to retry requests if the response is not received.


To create a message handler based on the request-response paradigm, use the `@MessagePattern()` decorator from `ascender.common.microservices`:
```python
from ascender.core import Controller, Get
from ascender.common.microservices import EventPattern, MessagePattern, Ctx

from dummy.user import UserResponse

@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(self):
        self.users = []
    
    @Get()
    async def main_endpoint(self):
        return "..."
    
    @EventPattern("user.created")
    async def user_created_event(self, data: UserResponse):
        # Do some user specific logic for user creation (e.g. save user into cache or something else)
        self.users.append(data) # WARN: avoid writing shared states in real project or use locks. This one is made for demonstration purposes only!
    
    @MessagePattern("users.get")
    async def get_users_rpc(self, ctx: Annotated[KafkaContext, Ctx()]) -> list[UserResponse]:
        print(ctx.offset, ctx.partition, ctx.correlation_id)
        return self.users
```

In this code, `get_users_rpc()` handler listens for messages that match `users.get` pattern.
The returned value will be returned to the producer side.

Also you may assign ctx to the message pattern, by default message pattern listens for `users.get` pattern in all defined transporters. But if you will assign ctx, you can assign it only for a specific transporter. In the example above, it's `Kafka`. So it will listen for `users.get` pattern only in kafka

## Client Proxy

To interact with other microservices as client, you can use `ClientProxy` class from `ascender.common.microservices`.
To inject `ClientProxy` you have to use that `token` we earlier talked about.

As you remember, earlier we defined TCP transport connection in `provideMicroservices` and we set `main` as token of the transport connection. Now let's inject `ClientProxy` of that transporter:
```python
from ascender.core import Controller, Inject
from ascender.common.microservices import ClientProxy

@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(
        self,
        main_client: Annotated[ClientProxy, Inject("main")],
    ):
        self.main_client = main_client
```

`ClientProxy` exposes two primary methods:

- **`send`** – send a message pattern and wait for an acknowledgment (RPC style).
- **`emit`** – emit an event pattern without waiting for any acknowledgment.

### Emitting Events

To emit an event to the event pattern of other microservice or consumers you can use `emit()` method of the `ClientProxy`.

```python
from ascender.core import Controller, Inject, Post
from ascender.common.microservices import ClientProxy
from dummy.users import UserDTO

@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(
        self,
        main_client: Annotated[ClientProxy, Inject("main")],
    ):

    @Post("create-user")
    async def create_user(self, user: UserDTO):
        # Do some user creation logic
        await self.main_client.emit("user.created", user)
```

In this example we emit event by `user.created` pattern, when user will be created for example in **Users** microservice.

`user.created` event pattern we defined earlier will now receive the event we emitted and `UserDTO` we passed. Though usually we had to pass `UserResponse`. Make sure that data you're passing match each other or `EventPattern` will raise an exception and data will be lost.

### Sending Messages

To send message following request-response paradigm, you can use `send` method of the `ClientProxy` if you need send & wait for response behaviour.

```python
from ascender.core import Controller, Inject, Post
from ascender.common.microservices import ClientProxy
from dummy.users import UserResponse

@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(
        self,
        main_client: Annotated[ClientProxy, Inject("main")],
    ):

    @Get("users")
    async def gets_users(self):
        users = await self.main_client.send("users.get", response_type=list[UserResponse])

        return users
```

This code snippet sends `users.get` message pattern and waits for response, if it didn't receive any response within timeout scope which's 10 seconds by default, it will raise `TimeoutError`.

There's also another way of handling messages. If you want more reactivity and handling responses by using callbacks you can use [ReactiveX](https://github.com/ReactiveX/RxPY?tab=readme-ov-file) (Also known as RxPY) observables to achieve this.

To send message in a reactive way, you can use `send_as_observable()` method of the `ClientProxy` object.

For example, let's make an event that always updates and actualizes caches when `cache.update` pattern will be emitted:
```python
from ascender.core import Controller, Inject, Post
from ascender.common.microservices import ClientProxy
from dummy.users import UserResponse
from dummy.cache_service import CacheService

import asyncio

@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(
        self,
        main_client: Annotated[ClientProxy, Inject("main")],
        logger: Annotated[Logger, Inject("ASC_LOGGER")],
        cache_service: CacheService,
    ):

    @EventPattern("cache.update")
    async def update_cache(self):
        users = await self.main_client.send_as_observable("users.get", response_type=list[UserResponse])
        users.subscribe(
            on_next=lambda response: asyncio.create_task(self.cache_service.update_users(response)),
            on_error=lambda err: self.logger.error(err)
        )
```
