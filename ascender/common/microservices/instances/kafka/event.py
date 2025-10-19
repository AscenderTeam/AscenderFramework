from typing import TYPE_CHECKING
from ascender.common.microservices.abc.event_transport import EventTransport
from ascender.common.microservices.utils.data_parser import parse_data

if TYPE_CHECKING:
    from ascender.common.microservices.instances.kafka.client import KafkaClient
    from ascender.common.microservices.instances.kafka.transporter import KafkaTransporter


class KafkaEventTransport(EventTransport):
    def __init__(self, transport: "KafkaTransporter | KafkaClient"):
        super().__init__(transport)

    async def send_event(self, pattern, data = None, **kwargs):
        data = parse_data(data)
        return await self.transport.producer.send(pattern, value=data.encode(), **kwargs)
    
    async def send_event_with_defer(self, pattern, data = None, **kwargs):
        return await self.transport.producer.send_and_wait(pattern, value=data, **kwargs)