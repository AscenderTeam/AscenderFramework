from inspect import isclass
from typing import Any, TypeVar
from ascender.common.microservices.abc.client_proxy import ClientProxy, Undefined
from ascender.common.microservices.instances.redis.event import RedisEventTransport
from ascender.common.microservices.instances.redis.rpc import RedisRPCTransport
from ascender.common.microservices.utils.data_parser import validate_python
from reactivex import operators as ops

T = TypeVar("T")


class RedisClient(ClientProxy):
    def __init__(self, event_bus, configs: dict = {}, instance=None):
        super().__init__(event_bus, configs, instance)
        try:
            import redis.asyncio as redis
        except ImportError as e:
            raise ImportError(
                "Redis transporter requires the 'redis' package. Install it with 'pip install redis'."
            ) from e

        self.redis = redis
        if not instance:
            self.client = self.redis.from_url(self.configs.get("redis_url", "redis://localhost"))
        else:
            self.client = instance.transporter.publisher

    async def connect(self):
        if not self.instance:
            self.rpc_transport = RedisRPCTransport(self)
            self.event_transport = RedisEventTransport(self)
        else:
            self.rpc_transport = self.instance.transporter.rpc_transport
            self.event_transport = self.instance.transporter.event_transport

    async def disconnect(self):
        if not self.instance and self.client:
            await self.client.close()

    async def send(
        self,
        pattern: str,
        data: Any = None,
        timeout: float = 20.0,
        response_type: type[T] | type[Undefined] = Undefined,
    ):
        response = await self.rpc_transport.send_request(pattern=pattern, data=data, timeout=timeout)
        if isclass(response_type) and issubclass(response_type, Undefined):
            return response
        response = validate_python(response, response_type)
        return response

    async def send_as_observable(
        self,
        pattern: str,
        data: Any = None,
        timeout: float = 20.0,
        response_type: type[T] = Any,
    ):
        observable = await self.rpc_transport.send_nack_request(pattern=pattern, data=data, timeout=timeout)
        return observable.pipe(
            ops.map(lambda res: validate_python(res, response_type))
        )

    async def emit(self, pattern: str, data: Any = None, **kwargs):
        return await self.event_transport.send_event(pattern=pattern, data=data, **kwargs)

    def unwrap(self, rtype: type[T]) -> T:
        from redis.asyncio import Redis
        if not isclass(rtype):
            raise TypeError(f"Unknown transporter instance type {rtype}")
        if issubclass(rtype, Redis):
            return self.client
        raise TypeError(f"Unknown transporter instance type {rtype.__name__}")