import json
import traceback
from inspect import isclass
from typing import TypeVar

from ascender.common.microservices.abc.transporter import BaseTransporter
from ascender.common.microservices.instances.redis.context import RedisContext
from ascender.common.microservices.instances.redis.event import RedisEventTransport
from ascender.common.microservices.instances.redis.rpc import RedisRPCTransport

T = TypeVar("T")


class RedisTransporter(BaseTransporter):
    """
    Redis Transporter implementation working on ascender framework's default request correlation model.
    
    Supports both RPC and Event message patterns.

    Raises:
        TypeError: If the requested underlying transporter instance type is unknown.
    """
    is_stopped: bool = True

    def __init__(self, instance, event_bus, configs: dict = {}):
        super().__init__(instance, event_bus, configs)
        # Lazy import of redis.asyncio for import safety.
        try:
            import redis.asyncio as redis
        except ImportError as e:
            raise ImportError(
                "Redis transporter requires the 'redis' package. Install it with 'poetry add redis'."
            ) from e

        self.redis = redis
        self.redis_url = self.configs.get("redis_url", "redis://localhost")
        # Create one connection for publishing...
        self.publisher = None  # Will hold the Redis connection.
        # ...and a PubSub object for subscribing.
        self.subscriber = None

        self.rpc_transport = RedisRPCTransport(self)
        self.event_transport = RedisEventTransport(self)

    async def listen(self):
        """
        Called when the server starts.
        Creates a single connection for publishing and derives a PubSub subscriber
        for channels based on the event bus subscriptions.
        """
        from redis.exceptions import ConnectionError
        self.is_stopped = False
        self.publisher = self.redis.from_url(self.redis_url, **self.configs.get("publisher", {}))
        self.subscriber = self.publisher.pubsub(**self.configs.get("subscriber", {}))

        channels = [
            pattern for pattern in self.event_bus._subscriptions if "*" not in pattern]
        if channels:
            await self.subscriber.subscribe(*channels)
        try:
            async for message in self.subscriber.listen():
                try:
                    if message["type"] != "message":
                        continue
                    # Redis messages are dicts like:
                    #   {"type": "message", "channel": b"channel", "data": b"payload"}
                    channel = message.get("channel")
                    data = message.get("data").decode()

                    if not data:
                        continue

                    metadata = {
                        "pattern": channel.decode() if isinstance(channel, bytes) else channel,
                        "transporter": "redis",
                    }
                    try:
                        envelope = json.loads(data)
                        correlation_id = envelope.get("correlationId")
                        raw_data = envelope.get("payload", data)
                    except Exception:
                        correlation_id = None
                        raw_data = data

                    context = RedisContext(
                        correlation_id=correlation_id,
                        is_event=not bool(correlation_id),
                        rpc_transport=self.rpc_transport,
                        event_transport=self.event_transport,
                        pattern=metadata["pattern"],
                        channel=metadata["pattern"],
                    )
                    await self.event_bus.emit(context, metadata["pattern"], raw_data, metadata)
                except Exception:
                    traceback.print_exc()
        except ConnectionError:
            pass

    async def close(self):
        """Closes the Redis connection."""
        self.is_stopped = True
        if self.publisher:
            await self.publisher.aclose(close_connection_pool=True)
        if self.subscriber:
            await self.subscriber.aclose()

    def unwrap(self, rtype: type[T]) -> T:
        """
        Returns the underlying Redis connection if requested.
        """
        if not isclass(rtype):
            raise TypeError(f"Unknown transporter instance type {rtype}")
        from redis.asyncio import Redis
        if issubclass(rtype, Redis):
            return self.publisher
        raise TypeError(f"Unknown transporter instance type {rtype.__name__}")
