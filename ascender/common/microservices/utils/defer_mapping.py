from logging import getLogger
from typing import Any
from reactivex import of, timer, never, throw


def kafka_defer(timeout: float, correlation_id: str):
    def wrapper(item: tuple[str, Any, dict]):
        logger = getLogger("Ascender Framework")
        if item[0] == f"defer-{correlation_id}":
            logger.debug("RPC defer has been requested, deferring response for additional seconds!")
            return timer(timeout + timeout)
        
        if item[0] == f"response-{correlation_id}":
            return of(None)
        
        return timer(timeout)
    
    return wrapper