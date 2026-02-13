from ascender.common import Injectable
from ascender.core import LifecycleService


@Injectable(provided_in="root")
class LifecycleTestService(LifecycleService):
    def __init__(self):
        print("Initialized the service correctly")

    async def on_startup(self):
        print("LifecycleTestService: on_startup")

    async def on_shutdown(self):
        print("LifecycleTestService: on_shutdown")