from controllers.thematics.models import ThematicDTO
from controllers.thematics.repository import ThematicsRepo
from controllers.thematics.service import ThematicsService
from core.types import ControllerModule
from core.utils.controller import Controller, Get, Post
from entities.dialogue import ThematicEntity

@Controller()
class Thematics:
    def __init__(self, thematics_service: ThematicsService) -> None:
        self.thematics = thematics_service

    @Post()
    async def create_thematic_endpoint(self, dto: ThematicDTO):
        return await self.thematics.create_thematic(dto)
    
    @Get()
    async def get_thematics_endpoint(self, project_id: int):
        return await self.thematics.get_thematics(project_id)
    
    @Get("{thematic_id}")
    async def get_thematic_endpoint(self, thematic_id: int):
        return await self.thematics.get_thematic(thematic_id)


def setup() -> ControllerModule:
    return {
        "controller": Thematics,
        "services": {
            "thematics": ThematicsService
        },
        "repository": ThematicsRepo,
        "repository_entities": {
            "thematics": ThematicEntity,
        }
    }