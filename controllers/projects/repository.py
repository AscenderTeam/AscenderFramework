from core.extensions.repositories import Repository
from entities.projects import ProjectEntity, ProjectStructureEntity


class ProjectsRepo(Repository):
    def __init__(self, projects: ProjectEntity, project_structures: ProjectStructureEntity) -> None:
        self.projects = projects
        self.project_structures = project_structures
    
    async def get_all(self):
        return await self.projects.all()
    
    async def get_one(self, **filter):
        return await self.projects.filter(**filter).first()
    
    async def get_project_structure(self, project_id: int):
        return await self.project_structures.filter(project_id=project_id).first()
    
    async def new_project(self, **data):
        return await self.projects.create(**data)
    
    async def create_project_structure(self, project_id: int, data: dict):
        return await self.project_structures.create(project_id=project_id, data=data)