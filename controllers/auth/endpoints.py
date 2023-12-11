from fastapi import Depends
from controllers.auth.repository import AuthRepo
from controllers.auth.service import AuthService
from core.guards.authenticator import IsAuthenticated
from core.types import ControllerModule
from core.utils.controller import Controller, Get
from core.extensions.authentication import AscenderAuthenticationFramework

@Controller()
class Auth:
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service
        self.auth_provider = AscenderAuthenticationFramework.auth_provider

    @Get("login")
    async def login(self, login: str, password: str):
        return await self.auth_provider.authenticate(login, password)

    @Get()
    async def get_auth_endpoint(self, token: str):
        return await self.auth_provider.get_authenticated_user(token)
        return self.auth_service.get_hello()



def setup() -> ControllerModule:
    return {
        "controller": Auth,
        "services": {
            "auth": AuthService
        },
        "repository": AuthRepo,
        "repository_entities": {
            # Add your entities here...
        }
    }
