import asyncio
from functools import wraps
from typing import Coroutine

# -*- coding: utf-8 -*- #


class CoroCLI:
    """
    Wrapping decorator using functools to execute coroutine function of CLI class.
    """

    def __init__(self, is_tortoise: bool = False):
        self.is_tortoise = is_tortoise

    def __call__(self, func: Coroutine[any, any, any]):

        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Executing coroutine...")
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            try:
                task = loop.run_until_complete(func(*args, **kwargs))

            finally:
                if self.is_tortoise:
                    from tortoise import Tortoise
                    loop.run_until_complete(Tortoise.close_connections())
                # Only close if we are not in a running loop that we didn't create
                # But here we probably should not close it if it's the global one
                # Actually, the original code always closed it. 
                # To be safe and match original intent:
                if not loop.is_running():
                    loop.close()

            return task

        return wrapper
