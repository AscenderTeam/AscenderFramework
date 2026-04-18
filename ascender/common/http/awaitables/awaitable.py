import asyncio
from typing import Coroutine


def _await(coro: Coroutine):
    """
    Runs any coroutine in sync function, especially of the RxPY's Observable's `on_next` and `on_error` functions
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

__all__ = ["_await"]