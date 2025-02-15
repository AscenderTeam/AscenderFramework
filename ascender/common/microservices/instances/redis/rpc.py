import asyncio
import json
import traceback
from uuid import uuid4
from reactivex import Subject, operators as ops, throw, timer
from reactivex.scheduler.eventloop import AsyncIOScheduler

from ascender.common.microservices.abc.rpc_transport import RPCTransport
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.utils.data_parser import decode_message, parse_data
from ascender.common.microservices.utils.defer_mapping import kafka_defer  # (reuse defer mapper)
from ascender.common.microservices.utils.redis_tools import parse_redis_encodable
from ascender.core import inject
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ascender.common.microservices.instances.redis.context import RedisContext
    from ascender.common.microservices.instances.redis.transporter import RedisTransporter
    from ascender.common.microservices.instances.redis.client import RedisClient


class RedisRPCTransport(RPCTransport):
    def __init__(self, transport: "RedisTransporter | RedisClient"):
        super().__init__(transport)
        self.response_subject = Subject()
        self.logger = inject("ASC_LOGGER")

    async def send_request(self, pattern, data, timeout):
        loop = asyncio.get_running_loop()
        asyncio_scheduler = AsyncIOScheduler(loop)
        correlation_id = str(uuid4())
        response = asyncio.Future()
        response_received = asyncio.Event()

        payload = {
            "correlationId": correlation_id,
            "payload": parse_data(data),
        }
        message = json.dumps(payload)

        def define_response(resp: Any):
            if not response.done():
                response.set_result(resp)
            response_received.set()

        def throw_error(err: Exception):
            if not response.done():
                response.set_exception(err)
            response_received.set()

        subscription = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout_with_mapper(
                timer(timeout),
                kafka_defer(timeout, correlation_id),
                throw(TimeoutError("Response timed out."))
            ),
            ops.filter(lambda pair: pair[0] == f"response-{correlation_id}"),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        ).subscribe(
            on_next=define_response,
            on_error=throw_error,
        )

        self.logger.debug(f"Sending message to {pattern} with correlation ID {correlation_id}")
        await self.transport.publisher.publish(pattern, message)
        self.logger.info(f"Successfully sent message pattern {pattern}")
        self.logger.debug(f"Now waiting for response from pattern {pattern}")

        await response_received.wait()
        subscription.dispose()
        self.logger.info(f"Received response for pattern {pattern}")
        return await response

    async def send_nack_request(self, pattern, data, timeout):
        loop = asyncio.get_event_loop()
        asyncio_scheduler = AsyncIOScheduler(loop)
        correlation_id = str(uuid4())
        payload = {
            "correlationId": correlation_id,
            "payload": parse_data(data),
        }
        message = json.dumps(payload)
        await self.transport.publisher.publish(pattern, message)

        observable = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout_with_mapper(
                timer(timeout),
                kafka_defer(timeout, correlation_id),
                throw(TimeoutError("Response timed out."))
            ),
            ops.filter(lambda pair: pair[0] == f"response-{correlation_id}"),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        )
        return observable

    async def defer(self, pattern: str, correlation_id: str):
        self.logger.debug(f"Deferring response for pattern {pattern} with correlation ID {correlation_id}")
        payload = {
            "correlationId": f"defer-{correlation_id}",
            "payload": "defer",
        }
        message = json.dumps(payload)
        await self.transport.publisher.publish(pattern, message)

    async def send_response(self, pattern, correlation_id, response):
        self.logger.debug(f"Responding on pattern {pattern} with correlation ID {correlation_id}")
        try:
            message = parse_redis_encodable(correlation_id, response.decode())
            await self.transport.publisher.publish(pattern, message)
        except:
            traceback.print_exc()

    async def raise_exception(self, pattern, correlation_id, exception):
        if not isinstance(exception, RPCException):
            raise TypeError(f"Expected RPCException, got {exception.__class__.__name__}")
        payload = {
            "correlationId": correlation_id,
            "payload": json.dumps(exception.to_dict()),
        }
        message = json.dumps(payload)
        await self.transport.publisher.publish(pattern, message)

    async def process_response(self, correlation_id, response, **kwargs):
        if not correlation_id:
            return
        if not (correlation_id.startswith("response-") or correlation_id.startswith("defer-")):
            return
        try:
            decoded = decode_message(response)
        except Exception:
            decoded = response
        if isinstance(decoded, dict):
            if RPCException.is_exception(decoded):
                self.response_subject.on_error(RPCException.from_dict(decoded))
                return
        self.response_subject.on_next((correlation_id, decoded, kwargs))

    async def listen_for_requests(self, context: "RedisContext", data: Any, metadata: dict) -> None:
        if metadata.get("transporter") != "redis":
            return
        await self.process_response(context.correlation_id, data, **metadata)