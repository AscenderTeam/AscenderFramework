from __future__ import annotations

from types import SimpleNamespace
from typing import Annotated, Any, cast

import pytest
from pydantic import BaseModel

from ascender.common.microservices.types import AckStatus, RequestType
from ascender.common.microservices.types.ctx import Ctx
from ascender.common.microservices.utils.frames import decode_incoming_frame, serialize_frame
from ascender.common.microservices.utils.handler_signature import HandlerSignaturePlan
from ascender.common.microservices.pipes import Pipe, PipePayload
from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.exceptions.rpc_exception import RPCException


class SampleDTO(BaseModel):
    name: str
    age: int


def make_context(**overrides: Any) -> BaseContext:
    base = {
        "pattern": "users:create",
        "correlation_id": "abc123",
        "rpc_transport": cast(Any, object()),
        "event_transport": cast(Any, object()),
        "is_event": False,
    }
    base.update(overrides)
    return cast(BaseContext, SimpleNamespace(**base))


def pipe_upper(payload: PipePayload) -> Any:
    value = payload.value
    if isinstance(value, str):
        return value.upper()
    return value


def pipe_default_on_error(payload: PipePayload) -> int:
    if payload.parsing_error:
        return 0
    if isinstance(payload.value, int):
        return payload.value
    raise ValueError("unexpected value")


async def sample_handler(
    ctx: Annotated[BaseContext, Ctx()],
    dto: SampleDTO,
    note: Annotated[str, Pipe(pipe_upper)],
    retries: Annotated[int, Pipe(pipe_default_on_error)],
):
    return ctx, dto, note, retries


@pytest.mark.asyncio
async def test_handler_signature_parses_payload_and_context():
    plan = HandlerSignaturePlan(sample_handler)
    context = make_context()
    data = {
        "dto": {"name": "neo", "age": 42},
        "note": "ping",
        "retries": "not-a-number",
    }

    payload = await plan.resolve_payload(context, data)

    assert payload["ctx"] is context
    assert isinstance(payload["dto"], SampleDTO)
    assert payload["dto"].name == "neo"
    assert payload["note"] == "PING"
    assert payload["retries"] == 0


@pytest.mark.asyncio
async def test_handler_signature_requires_missing_field():
    async def handler(dto: SampleDTO):
        return dto

    plan = HandlerSignaturePlan(handler)
    context = make_context()

    with pytest.raises(RPCException) as excinfo:
        await plan.resolve_payload(context, {"dto": {"age": "invalid"}})
    message = str(excinfo.value)
    assert "SampleDTO" in message
    assert "Field required" in message


def test_decode_incoming_frame_for_legacy_ack():
    payload = {"result": "ok"}
    frame = decode_incoming_frame(
        payload,
        correlation_id="response-xyz",
        default_type=RequestType.CALL,
    )

    assert frame.request_type == RequestType.ACK
    assert frame.correlation_id == "xyz"
    assert frame.ack_status == AckStatus.OK
    assert frame.payload == payload


def test_serialize_and_decode_roundtrip():
    raw = serialize_frame(
        request_type=RequestType.CALL,
        payload={"ping": True},
        correlation_id="abc",
    )
    frame = decode_incoming_frame(raw, correlation_id="abc", default_type=RequestType.CALL)
    assert frame.request_type == RequestType.CALL
    assert frame.correlation_id == "abc"
    assert frame.payload == {"ping": True}