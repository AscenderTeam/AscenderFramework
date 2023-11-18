from controllers.app.repository import AppRepo
from controllers.app.service import AppService
from core.types import ControllerModule
from core.utils.controller import Controller, Get

@Controller()
class App:
    def __init__(self, app_service: AppService) -> None:
        self.app_service = app_service

    @Get()
    async def get_app_endpoint(self):
        return self.app_service.get_hello()



def setup() -> ControllerModule:
    return {
        "controller": App,
        "services": {
            "app": AppService
        },
        "repository": AppRepo,
        "repository_entities": {
            # Add your entities here...
        }
    }
