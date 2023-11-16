from fastapi import HTTPException
from github import Github
from controllers.projects.models import ProjectDTO
from controllers.projects.serializers import PaginationSerializer, ProjectSerializer
from controllers.thematics.models import ThematicDTO
from controllers.thematics.service import ThematicsService
from core.extensions.services import Service
from controllers.projects.repository import ProjectsRepo


class ProjectsService(Service):
    
    thematics: ThematicsService

    def __init__(self, repository: ProjectsRepo) -> None:
        self._repository = repository
        self.git = Github("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")
    
    def __mounted__(self):
        self.define_thematics()

    def define_thematics(self):
        self.inject_controller("thematics", "thematics")

    async def get_projects(self, page: int = 1, page_size: int = 10):
        projects = await self._repository.projects.filter().offset((page - 1) * page_size).limit(page_size).all()
        count = await self._repository.projects.all().count()
        response = PaginationSerializer(total=int(count / page_size), current_page=page, page_size=page_size, entities=projects)
        return response()
    
    async def get_project(self, project_id: int):
        return await self._repository.get_one(id=project_id)
    
    async def create_project(self, data: ProjectDTO):
        try:
            repo = self.git.get_repo(data.github_url)
            project = await self._repository.new_project(**data.model_dump())
            
            ## Have to get structure of project
            await self._repository.create_project_structure(project.id, {})

            ## Creating first thematics
            await self.thematics.create_thematic(ThematicDTO(name="Getting started", issue=data.getting_started_prompt, filename="", project_id=project.id))

            return ProjectSerializer(project)()

        except Exception as e:
            raise HTTPException(404, "Invalid GitHub url!")