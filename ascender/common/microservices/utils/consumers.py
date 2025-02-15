import asyncio
import traceback
from typing import TYPE_CHECKING, Any

# from aiokafka import AIOKafkaConsumer
# from redis.asyncio.client import PubSub

from ascender.common.microservices.instances.bus import SubscriptionEventBus
from ascender.common.microservices.utils.redis_tools import decode_redis_data, parse_redis_encodable

if TYPE_CHECKING:
    from ascender.common.microservices.instances.transport import TransportInstance


async def consume_kafka(instance: "TransportInstance", consumer, event_bus: SubscriptionEventBus):
    consumer.subscribe(topics=tuple([pattern for pattern in event_bus._subscriptions if "*" not in pattern]))
    # await consumer.subscribe("dragon.kill")

    async for message in consumer:
        if message:
            # TODO: Add logging for debug and info
            await event_bus.emit(instance, message.topic, message.value, {
                "type": "kafka",
                "pattern": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "key": message.key,
                "timestamp": message.timestamp,
                "timestamp_type": message.timestamp_type
            })


async def consume_redis(instance: "TransportInstance", consumer, event_bus: SubscriptionEventBus, interval: float = 0.01):
    await consumer.subscribe(*[pattern for pattern in event_bus._subscriptions if "*" not in pattern])
    # await p.psubscribe(*[pattern for pattern in event_bus._subscriptions if "*" in pattern])
    async for message in consumer.listen():
        if message["type"] not in ["message", "pmessage"]:
            continue
        
        # TODO: Add logging for debug and info
        try:
            data = decode_redis_data(message["data"])
            await event_bus.emit(instance, message["channel"], data["data"], {
                "type": "redis", 
                "pattern": message['channel'],
                "event_type": message['type'], 
                "key": data["key"]
            })
        except Exception as e:
            traceback.print_exc()