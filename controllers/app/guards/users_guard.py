from ascender.guards import Guard
from fastapi import HTTPException, Request

from controllers.app.app_service import AppService


class UsersGuard(Guard):
    def __init__(self, default_http_error: int = 404):
        """
        Use __init__ for accepting parameters of guard decorator
        """
        self.default_http_error = default_http_error
    
    def __post_init__(self, app_service: AppService):
        """
        Handle dependency injections, use for injecting DIs
        """
        self.app_service = app_service
    
    async def can_activate(self, request: Request):
        """
        Works same as FastAPI's Dependency Injection
        """
        if not await self.app_service.get_users():
            print("Guard works")
            raise HTTPException(self.default_http_error)
        
