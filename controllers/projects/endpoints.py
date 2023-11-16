from controllers.projects.models import ProjectDTO
from controllers.projects.repository import ProjectsRepo
from controllers.projects.service import ProjectsService
from core.types import ControllerModule
from core.utils.controller import Controller, Get, Post
from entities.projects import ProjectEntity, ProjectStructureEntity

@Controller()
class Projects:
    def __init__(self, projects_service: ProjectsService) -> None:
        self.projects_service = projects_service

    @Get()
    async def get_projects_endpoint(self):
        return await self.projects_service.get_projects()
    
    @Get("{project_id}")
    async def get_project_endpoint(self, project_id: int):
        return await self.projects_service.get_project(project_id)
    
    @Post()
    async def create_project_endpoint(self, data: ProjectDTO):
        return await self.projects_service.create_project(data)


def setup() -> ControllerModule:
    return {
        "controller": Projects,
        "services": {
            "projects": ProjectsService
        },
        "repository": ProjectsRepo,
        "repository_entities": {
            "projects": ProjectEntity,
            "project_structures": ProjectStructureEntity
        }
    }