from __future__ import annotations

from enum import Enum


class RequestType(str, Enum):
    """Represents the intent of an incoming microservice message."""

    CALL = "call"
    EVENT = "event"
    ACK = "ack"


class AckStatus(str, Enum):
    """Additional status metadata for acknowledgement (ACK) frames."""

    OK = "ok"
    ERROR = "error"
    DEFER = "defer"


__all__ = ["RequestType", "AckStatus"]
