from core.extensions.repositories import Repository
from core.extensions.services import Service


class UsersService(Service):
    def __init__(self, repository: Repository) -> None:
        super().__init__(repository)
    
    async def get_user(self, user_id: int) -> dict:
        return await self._repository.get_user(user_id)
    
    async def get_users(self) -> list:
        return await self._repository.get_users()
    
    async def create_user(self) -> dict:
        return await self._repository.create_user()