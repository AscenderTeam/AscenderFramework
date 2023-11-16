from core.extensions.repositories import Repository
from entities.dialogue import ThematicEntity


class ThematicsRepo(Repository):
    def __init__(self, thematics: ThematicEntity) -> None:
        self.thematics = thematics
    
    async def get_all(self):
        return await self.thematics.all()
    
    async def get_one(self, **filter):
        return await self.thematics.filter(**filter).first()
        
    async def new_thematic(self, **data):
        return await self.thematics.create(**data)

    async def get_thematics(self, project_id: int):
        return await self.thematics.filter(project_id=project_id).all()