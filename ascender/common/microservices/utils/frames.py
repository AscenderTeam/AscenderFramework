from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from ascender.common.microservices.types import AckStatus, RequestType
from ascender.common.microservices.utils.data_parser import parse_data


@dataclass(slots=True)
class IncomingFrame:
    """Normalized representation of an incoming microservice frame."""

    request_type: RequestType
    payload: Any
    correlation_id: str | None
    ack_status: AckStatus | None = None
    raw_envelope: Any | None = None


def _decode_payload(data: Any) -> Any:
    if data is None:
        return None
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8")
        except Exception:
            data = data.decode("utf-8", errors="ignore")
    if isinstance(data, str):
        stripped = data.strip()
        if not stripped:
            return ""
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return data
    return data


def _normalize_payload(value: Any) -> Any:
    serialized = parse_data(value)
    try:
        return json.loads(serialized)
    except json.JSONDecodeError:
        return serialized


def serialize_frame(
    request_type: RequestType,
    payload: Any,
    *,
    correlation_id: str | None = None,
    ack_status: AckStatus | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    frame: dict[str, Any] = {
        "type": request_type.value,
        "payload": _normalize_payload(payload),
    }
    if correlation_id is not None:
        frame["correlationId"] = correlation_id
    if ack_status is not None:
        frame["ackStatus"] = ack_status.value
    if metadata:
        frame["metadata"] = metadata
    return json.dumps(frame)


def decode_incoming_frame(
    raw: Any,
    *,
    correlation_id: str | None,
    default_type: RequestType,
) -> IncomingFrame:
    decoded = _decode_payload(raw)
    if isinstance(decoded, dict):
        type_value = decoded.get("type")
        if isinstance(type_value, str) and type_value in RequestType._value2member_map_:
            ack_status_value = decoded.get("ackStatus")
            ack_status = None
            if isinstance(ack_status_value, str) and ack_status_value in AckStatus._value2member_map_:
                ack_status = AckStatus(ack_status_value)
            return IncomingFrame(
                request_type=RequestType(type_value),
                payload=decoded.get("payload"),
                correlation_id=decoded.get("correlationId", correlation_id),
                ack_status=ack_status,
                raw_envelope=decoded,
            )
    normalized_id = normalize_correlation_id(correlation_id)
    derived_type = default_type
    derived_ack = None
    if correlation_id:
        if correlation_id.startswith("response-"):
            derived_type = RequestType.ACK
            derived_ack = AckStatus.OK
        elif correlation_id.startswith("defer-"):
            derived_type = RequestType.ACK
            derived_ack = AckStatus.DEFER
    return IncomingFrame(
        request_type=derived_type,
        payload=decoded,
        correlation_id=normalized_id,
        ack_status=derived_ack,
        raw_envelope=decoded,
    )


def normalize_correlation_id(value: str | None) -> str | None:
    if not value:
        return value
    for prefix in ("response-", "defer-"):
        if value.startswith(prefix):
            return value[len(prefix) :]
    return value


def serialize_ack_payload(message: Any = None) -> Any:
    if message is None:
        return {"ack": True}
    return message


def normalize_payload(value: Any) -> Any:
    """Public helper for transports to normalize arbitrary payloads."""

    return _normalize_payload(value)


__all__ = [
    "IncomingFrame",
    "normalize_correlation_id",
    "decode_incoming_frame",
    "serialize_frame",
    "serialize_ack_payload",
    "normalize_payload",
]
