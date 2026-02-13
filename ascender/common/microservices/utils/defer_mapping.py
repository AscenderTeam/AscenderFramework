from logging import getLogger
from typing import Any

from reactivex import of, timer

from ascender.common.microservices.types import AckStatus


def kafka_defer(timeout: float, correlation_id: str):
    def wrapper(item: tuple[str, Any, dict]):
        logger = getLogger("Ascender Framework")
        metadata = item[2] if len(item) > 2 else {}
        ack_status = metadata.get("ackStatus")
        if ack_status == AckStatus.DEFER:
            logger.debug("RPC defer has been requested, deferring response for additional seconds!")
            return timer(timeout + timeout)
        return of(None)

    return wrapper