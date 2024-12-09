from ascender.guards import ParamGuard
from fastapi import Request

from controllers.app.app_service import AppService


class AuthGuard(ParamGuard):
    def __init__(self):
        """
        Use __init__ for accepting parameters of guard decorator
        """
        ...
    
    def __post_init__(self, app_service: AppService):
        """
        Handle dependency injections, use for injecting DIs
        """
        self.app_service = app_service
        
    async def users_guard(self, request: Request):
        """
        user _description
        """
        return await self.app_service.get_users()
    