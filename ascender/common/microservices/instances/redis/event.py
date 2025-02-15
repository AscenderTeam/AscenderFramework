import json
from ascender.common.microservices.abc.event_transport import EventTransport
from ascender.common.microservices.utils.data_parser import parse_data
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ascender.common.microservices.instances.redis.client import RedisClient
    from ascender.common.microservices.instances.redis.transporter import RedisTransporter


class RedisEventTransport(EventTransport):
    def __init__(self, transport: "RedisTransporter | RedisClient"):
        super().__init__(transport)

    async def send_event(self, pattern, data=None, **kwargs):
        message = json.dumps({"payload": parse_data(data)})
        return await self.transport.publisher.publish(pattern, message)

    async def send_event_with_defer(self, pattern, data=None, **kwargs):
        message = json.dumps({"payload": parse_data(data)})
        return await self.transport.publisher.publish(pattern, message)