from abc import ABC, abstractmethod


class Service:
    pass


class LifecycleService(ABC):
    @abstractmethod
    async def on_startup(self):
        ...

    @abstractmethod
    async def on_shutdown(self):
        ...