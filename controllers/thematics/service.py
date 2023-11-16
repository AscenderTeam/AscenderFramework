from fastapi import HTTPException
from controllers.thematics.models import ThematicDTO
from core.extensions.services import Service
from controllers.thematics.repository import ThematicsRepo


class ThematicsService(Service):
    def __init__(self, repository: ThematicsRepo) -> None:
        self._repository = repository
    
    async def create_thematic(self, dto: ThematicDTO):
        """
        ## Creates thematic

        Args:
            dto (ThematicDTO): Input data to create thematic
        """
        return await self._repository.new_thematic(**dto.model_dump())

    async def get_thematics(self, project_id: int):
        """
        ## Get all thematics

        Args:
            project_id (int): ID of project
        """
        return await self._repository.get_thematics(project_id)
    
    async def get_thematic(self, thematic_id: int):
        """
        ## Get one thematic

        Args:
            thematic_id (int): ID of thematic
        """
        thematic = await self._repository.get_one(id=thematic_id)

        if not thematic:
            raise HTTPException(status_code=404, detail="Thematic not found")
        
        return thematic