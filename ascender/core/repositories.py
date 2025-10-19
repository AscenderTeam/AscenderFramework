from ascender.core.database import AppDBContext
from ascender.core.di.abc.base_injector import Injector


class Repository:
    _injector: Injector
    
    def __init__(self, _context: AppDBContext | None = None) -> None:
        self._context = _context
    

class IdentityRepository(Repository):
    
    async def create_user(self, *args, **kwargs):
        raise NotImplementedError()
    
    async def update_user(self, *args, **kwargs):
        raise NotImplementedError()
    
    async def delete_user(self, *args, **kwargs):
        raise NotImplementedError()
    
    async def get_user(self, user_id: int):
        raise NotImplementedError()