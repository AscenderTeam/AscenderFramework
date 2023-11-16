from controllers.users.service import UsersService
from core.types import ControllerModule
from core.utils.controller import Controller, Get
from entities.users import UserEntity

@Controller()
class Users:
    def __init__(self, users_service: UsersService) -> None:
        self.users = users_service
    
    @Get("github")
    async def get_github_users_endpoint(self):
        return await self.users.get_github_users()

def setup() -> ControllerModule:
    return {
        "controller": Users,
        "services": {
            "users": UsersService,
        },
        "repository": None,
        "repository_entities": {
            "user": UserEntity
        }
    }