from fastapi import Depends
from controllers.auth.models import LoginDTO, UserDTO, UserResponse
from controllers.auth.repository import AuthRepo
from controllers.auth.service import AuthService
from core.extensions.authentication.entity import UserEntity
from core.extensions.serializer import Serializer
from core.guards.authenticator import GetAuthenticatedUser, IsAuthenticated
from core.types import ControllerModule
from core.utils.controller import Controller, Delete, Get, Post

@Controller()
class Auth:
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    @Post("login")
    async def login(self, user: LoginDTO):
        return await self.auth_service.auth_provider.authenticate(user.username, user.password.get_secret_value())

    @Post("register")
    async def register(self, user: UserDTO):
        return await self.auth_service.create_user(user)

    @Get("me")
    async def get_auth_endpoint(self, user: UserEntity = Depends(GetAuthenticatedUser(True))):
        return Serializer(UserResponse, user)()

    @Delete("{user_id}", dependencies=[Depends(IsAuthenticated(True))])
    async def delete_user_endpoint(self, user_id: int):
        return await self.auth_service.delete_user(user_id)

    ## SocketIO authentication support... In case of using SocketIO, uncomment the following code
    ## To enable SocketIO support, add this piece of code `app.use_sio()` in `bootstrap.py`
    # @Listen("connect", all_namespaces=True)
    # @IsAuthenticatedSocket()
    # async def socket_auth_endpoint(self, ctx):
    #     await ctx.emit("status", "Successfully connected")


def setup() -> ControllerModule:
    return {
        "controller": Auth,
        "services": {
            "auth": AuthService
        },
        "repository": AuthRepo,
        "repository_entities": {
            # Add your entities here...
        },
        "plugin_configs": {}
    }
