from core.extensions.services import Service
from controllers.app.repository import AppRepo


class AppService(Service):

    def __init__(self, repository: AppRepo) -> None:
        self._repository = repository
        
    
    async def get_hello(self):
        return "test"