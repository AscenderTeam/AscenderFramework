from enum import Enum
from typing import Any, TypedDict

from ascender.common.microservices.instances.kafka.client import KafkaClient
from ascender.common.microservices.instances.kafka.transporter import KafkaTransporter
from ascender.common.microservices.instances.redis.client import RedisClient
from ascender.common.microservices.instances.redis.transporter import RedisTransporter
from ascender.common.microservices.instances.tcp.client import TCPClient
from ascender.common.microservices.instances.tcp.transporter import TCPTransporter


class Transports(Enum):
    REDIS = RedisTransporter
    KAFKA = KafkaTransporter
    TCP = TCPTransporter


class Transport(TypedDict):
    transport: Transports
    options: dict[str | float | int, Any]


TRANSPORT_PROXY_MAPPING = {
    KafkaTransporter: KafkaClient,
    RedisTransporter: RedisClient,
    TCPTransporter: TCPClient
}