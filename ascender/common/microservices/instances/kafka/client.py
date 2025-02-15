from inspect import isclass
from typing import Any

from ascender.common.base.dto import BaseDTO
from ascender.common.base.response import BaseResponse
from ascender.common.microservices.abc.client_proxy import ClientProxy, Undefined, T
from ascender.common.microservices.instances.kafka.event import KafkaEventTransport
from ascender.common.microservices.instances.kafka.rpc import KafkaRPCTransport
from reactivex import operators as ops

from ascender.common.microservices.utils.data_parser import validate_python


class KafkaClient(ClientProxy):
    def __init__(self, event_bus, configs = ..., instance = None):
        super().__init__(event_bus, configs, instance)
        
        if not instance:
            from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
            self.consumer = AIOKafkaConsumer(**configs)
            self.producer = AIOKafkaProducer(**configs)
            return
        
        self.consumer = instance.transporter.consumer
        self.producer = instance.transporter.producer

    async def connect(self):
        if not self.instance:
            await self.consumer.start()
            await self.producer.start()
            self.rpc_transport = KafkaRPCTransport(self)
            self.event_transport = KafkaEventTransport(self)
            return
        
        self.rpc_transport = self.instance.transporter.rpc_transport
        self.event_transport = self.instance.transporter.event_transport
    
    async def disconnect(self):
        if not self.instance:
            await self.consumer.stop()
            await self.producer.stop()
    
    async def send(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0,
        response_type: type[T] | Any = Any,
    ):
        response = await self.rpc_transport.send_request(pattern=pattern, data=data, timeout=timeout)
        
        if isclass(response_type) and issubclass(response_type, Undefined):
            return response
        
        response = validate_python(response, response_type)
        
        return response
    
    async def send_as_observable(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0,
        response_type: type[T] = Any
    ):
        response = await self.rpc_transport.send_nack_request(pattern=pattern, data=data, timeout=timeout)

        return response.pipe(
            ops.map(lambda res: validate_python(res, response_type))
        )
    
    async def emit(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        **kwargs
    ):
        return await self.event_transport.send_event(pattern=pattern, data=data, **kwargs)
    
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