from typing import Any
from ascender.core.utils.controller import Controller, Get
from controllers.app.app_service import AppService
from controllers.app.guards.auth_guard import AuthGuard
from controllers.app.guards.users_guard import UsersGuard


@Controller(
    standalone=False,
    guards=[],
)
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service
    
    @Get()
    @AuthGuard()
    async def app_endpoint(self, users: list[Any]):
        return users