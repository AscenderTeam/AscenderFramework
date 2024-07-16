from controllers.auth.models import AuthDTO, UserDTO
from controllers.auth.repository import AuthRepo
from controllers.auth.service import AuthService
from core.identity.decorators.auth_refresher import AuthRefresher
from core.identity.decorators.authorize import Authorize
from core.identity.decorators.claim import Claim
from core.types import ControllerModule
from core.utils.controller import Controller, Get, Post


@Controller()
class Auth:
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    @Post("login")
    async def login(self, data: AuthDTO):
        return await self.auth_service.authenticate(data)

    @Post("register")
    async def register(self, data: UserDTO):
        return await self.auth_service.create_user(data)
    
    @Post("refresh-token")
    @AuthRefresher()
    async def refresh_token(self, credentials: tuple[str, str]):
        return {"access_token": credentials[0], "refresh_token": credentials[1],
                "type": "bearer"}

    @Get("me")
    @Authorize("isUser")
    @Claim()
    async def user_information(self, user_claim: dict):
        return await self.auth_service.get_user(user_claim["user_id"])


def setup() -> ControllerModule:
    return {
        "controller": Auth,
        "services": {
            "auth": AuthService
        },
        "repository": AuthRepo,
        "plugin_configs": {
            # Configuration for plugins here...
        },
    }
