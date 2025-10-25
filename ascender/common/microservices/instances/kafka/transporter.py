from inspect import isclass
import traceback
from typing import TypeVar

from ascender.common.microservices.abc.transporter import BaseTransporter
from ascender.common.microservices.instances.kafka.context import KafkaContext
from ascender.common.microservices.instances.kafka.event import KafkaEventTransport
from ascender.common.microservices.instances.kafka.metadata import KafkaMetadata
from ascender.common.microservices.instances.kafka.rpc import KafkaRPCTransport

T = TypeVar("T")


class KafkaTransporter(BaseTransporter):
    """
    Kafka Transporter implementation working on ascender framework's default request correlation model.
    
    Supports both RPC and Event message patterns.

    Raises:
        TypeError: If the requested underlying transporter instance type is unknown.
    """
    is_stopped: bool = True

    def __init__(self, instance, event_bus, configs = ...):
        super().__init__(instance, event_bus, configs)
        try:
            from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
        except ImportError as e:
            raise ImportError(
                "Kafka transporter requires the 'aiokafka' package. Install it with 'poetry add kafka'."
            ) from e
        self.consumer = AIOKafkaConsumer(**configs)
        self.producer = AIOKafkaProducer(**configs)
        
        self.rpc_transport = KafkaRPCTransport(self)
        self.event_transport = KafkaEventTransport(self)

    async def listen(self):
        """
        Being called each time when server starts
        """
        self.is_stopped = False
        await self.consumer.start()
        await self.producer.start()

        self.consumer.subscribe(topics=tuple([pattern for pattern in self.event_bus._subscriptions if "*" not in pattern]))

        async for message in self.consumer:
            if not message:
                continue

            try:
                metadata: KafkaMetadata = {
                    "headers": message.headers,
                    "pattern": message.topic,
                    "key": message.key,
                    "partition": message.partition,
                    "offset": message.offset,
                    "timestamp": message.timestamp,
                    "timestamp_type": message.timestamp_type,
                    "transporter": "kafka"
                }
                correlation_id = next((value.decode('utf-8') for key, value in metadata["headers"] if key == "correlationId"), None)
                context: KafkaContext = KafkaContext(
                    correlation_id=correlation_id, 
                    is_event=bool(correlation_id),
                    rpc_transport=self.rpc_transport,
                    event_transport=self.event_transport,
                    **metadata
                )
                await self.event_bus.emit(context, message.topic, message.value, metadata)
            except Exception as e:
                traceback.print_exc()
    
    async def close(self):
        """
        Being executed each times when server stops
        """
        await self.producer.stop()
        await self.consumer.stop()

        self.is_stopped = True
    
    def unwrap(self, rtype: type[T]) -> T:
        """
        If user needs this to be unwrapped
        """
        from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
        
        if not isclass(rtype):
            raise TypeError(f"Unknown transporter instance type {rtype}")
        
        if issubclass(rtype, AIOKafkaProducer):
            return self.producer
        
        if issubclass(rtype, AIOKafkaConsumer):
            return self.consumer
        
        raise TypeError(f"Unknown transporter instance type {rtype.__name__}")