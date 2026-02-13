import asyncio
import traceback
from uuid import uuid4
from reactivex import Subject, operators as ops, throw, timer
from reactivex.scheduler.eventloop import AsyncIOScheduler

from ascender.common.microservices.abc.rpc_transport import RPCTransport
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.types import AckStatus, RequestType
from ascender.common.microservices.utils.defer_mapping import kafka_defer  # (reuse defer mapper)
from ascender.common.microservices.utils.frames import (
    decode_incoming_frame,
    normalize_correlation_id,
    serialize_frame,
)
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

    async def _publish(self, channel: str, message: str) -> None:
        publisher = getattr(self.transport, "publisher", None)
        if publisher is None:
            raise RuntimeError("Redis publisher is not configured")
        await publisher.publish(channel, message)

    async def send_request(self, pattern, data, timeout):
        loop = asyncio.get_running_loop()
        asyncio_scheduler = AsyncIOScheduler(loop)
        correlation_id = str(uuid4())
        response = asyncio.Future()
        response_received = asyncio.Event()

        message = serialize_frame(
            request_type=RequestType.CALL,
            payload=data,
            correlation_id=correlation_id,
        )

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
            ops.filter(lambda pair: pair[0] == correlation_id),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        ).subscribe(
            on_next=define_response,
            on_error=throw_error,
        )

        self.logger.debug(f"Sending message to {pattern} with correlation ID {correlation_id}")
        await self._publish(pattern, message)
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
        message = serialize_frame(
            request_type=RequestType.CALL,
            payload=data,
            correlation_id=correlation_id,
        )
        await self._publish(pattern, message)

        observable = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout_with_mapper(
                timer(timeout),
                kafka_defer(timeout, correlation_id),
                throw(TimeoutError("Response timed out."))
            ),
            ops.filter(lambda pair: pair[0] == correlation_id),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        )
        return observable

    async def defer(self, pattern: str, correlation_id: str):
        self.logger.debug(f"Deferring response for correlation ID {correlation_id}")
        message = serialize_frame(
            request_type=RequestType.ACK,
            payload={"defer": True},
            correlation_id=correlation_id,
            ack_status=AckStatus.DEFER,
        )
        await self._publish("_rpc:response", message)

    async def send_response(self, pattern, correlation_id, response):
        self.logger.debug(f"Responding on pattern {pattern} with correlation ID {correlation_id}")
        try:
            message = serialize_frame(
                request_type=RequestType.ACK,
                payload=response,
                correlation_id=correlation_id,
                ack_status=AckStatus.OK,
            )
            await self._publish(pattern, message)
        except Exception:
            traceback.print_exc()

    async def raise_exception(self, pattern, correlation_id, exception):
        if not isinstance(exception, RPCException):
            raise TypeError(f"Expected RPCException, got {exception.__class__.__name__}")
        message = serialize_frame(
            request_type=RequestType.ACK,
            payload=exception.to_dict(),
            correlation_id=correlation_id,
            ack_status=AckStatus.ERROR,
        )
        await self._publish(pattern, message)

    async def process_response(self, correlation_id, response, **kwargs):
        if not correlation_id:
            return
        frame = decode_incoming_frame(
            response,
            correlation_id=correlation_id,
            default_type=RequestType.ACK,
        )
        normalized_id = normalize_correlation_id(frame.correlation_id)
        if frame.request_type != RequestType.ACK or normalized_id is None:
            return

        metadata = dict(kwargs)
        metadata["ackStatus"] = frame.ack_status

        if frame.ack_status == AckStatus.ERROR:
            if isinstance(frame.payload, dict) and RPCException.is_exception(frame.payload):
                self.response_subject.on_error(RPCException.from_dict(frame.payload))
            else:
                self.response_subject.on_error(RPCException(str(frame.payload)))
            return

        self.response_subject.on_next((normalized_id, frame.payload, metadata))

    async def listen_for_requests(self, context: "RedisContext", data: Any, metadata: dict) -> None:
        if metadata.get("transporter") != "redis":
            return
        if not context.correlation_id:
            return
        await self.process_response(context.correlation_id, data, **metadata)