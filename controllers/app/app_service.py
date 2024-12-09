from ascender.common import Injectable
from ascender.contrib.services import Service
from controllers.app.app_repository import AppRepo


@Injectable()
class AppService(Service):
    app_repo: AppRepo

    def __init__(self):
        ...
    
    async def create_user(self, name: str):
        return await self.app_repo.create_user(name=name)
    
    async def get_users(self):
        return await self.app_repo.get_users()